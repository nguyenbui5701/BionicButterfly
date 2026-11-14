"""Offline Tk adapter. Controls edit future scenario input, never output."""
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from bb_host_virtual_control_studio import StudioController
from bb_host_virtual_control_studio.session import KINDS, encode_session
from bb_host_virtual_control_studio.studio import BANNER, EFFORT_LABEL
try:
    from . import fixtures, offline
except ImportError:
    import fixtures, offline


class StudioWindow:
    def __init__(self, root, case='nominal'):
        self.root, self.controller = root, StudioController()
        self.bindings = fixtures.dependencies()
        root.title('Bionic Butterfly | Virtual Control Studio | MODEL ONLY')
        root.geometry('1180x850')
        root.minsize(950, 700)
        self.timer = None
        self._updating = False
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('Banner.TLabel', background='#442c16', foreground='#ffce7a', padding=12, font=('Segoe UI', 14, 'bold'))
        ttk.Label(root, text=BANNER, style='Banner.TLabel').pack(fill='x')
        ttk.Label(root, text=EFFORT_LABEL, padding=8).pack(fill='x')
        controls = ttk.Frame(root, padding=10)
        controls.pack(fill='x')
        self.preset = tk.StringVar(value=case)
        ttk.Combobox(controls, textvariable=self.preset, values=tuple(fixtures.CASES), state='readonly', width=14).grid(row=0, column=0)
        ttk.Button(controls, text='Load preset', command=self.load_preset).grid(row=0, column=1, padx=5)
        self.duration = tk.StringVar(value='195000')
        ttk.Label(controls, text='Duration (us)').grid(row=0, column=2)
        ttk.Entry(controls, textvariable=self.duration, width=12).grid(row=0, column=3)
        ttk.Button(controls, text='New empty session', command=self.new_session).grid(row=0, column=4, padx=5)
        ttk.Button(controls, text='Run entire simulation', command=self.replay).grid(row=0, column=5, padx=5)
        self.kind = tk.StringVar(value='CONTROL_VALID')
        self.at = tk.StringVar(value='200000')
        self.arm = tk.BooleanVar(value=False)
        self.flap = tk.IntVar(value=0)
        self.steer = tk.IntVar(value=0)
        ttk.Combobox(controls, textvariable=self.kind, values=KINDS, state='readonly', width=18).grid(row=1, column=0, pady=12)
        ttk.Label(controls, text='Original time (us)').grid(row=1, column=1)
        ttk.Entry(controls, textvariable=self.at, width=12).grid(row=1, column=2)
        ttk.Checkbutton(controls, text='ARM switch request', variable=self.arm).grid(row=1, column=3, columnspan=2)
        ttk.Button(controls, text='Append simulated event', command=self.append).grid(row=1, column=5)
        for row, label, var, low in ((2, 'Flap micro (0..1000000)', self.flap, 0), (3, 'Steering micro (-1000000..1000000)', self.steer, -1000000)):
            ttk.Label(controls, text=label).grid(row=row, column=0, columnspan=2, sticky='w')
            tk.Scale(controls, variable=var, from_=low, to=1000000, orient='horizontal', resolution=1, length=320).grid(row=row, column=2, columnspan=3, sticky='ew')
            ttk.Entry(controls, textvariable=var, width=12).grid(row=row, column=5)
        panes = ttk.Panedwindow(root, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=10)
        left, right = ttk.Frame(panes), ttk.Frame(panes)
        panes.add(left, weight=1); panes.add(right, weight=2)
        ttk.Label(left, text='Scenario actions (inputs only)').pack(anchor='w')
        self.actions = tk.Text(left, width=42, height=10, wrap='none', state='disabled')
        self.actions.pack(fill='both', expand=True)
        ttk.Label(right, text='Acknowledged MODEL timeline').pack(anchor='w')
        self.table = ttk.Treeview(right, columns=('time', 'state', 'rf', 'effort'), show='headings', height=10)
        for name, width in (('time', 75), ('state', 180), ('rf', 80), ('effort', 140)):
            self.table.heading(name, text=name); self.table.column(name, width=width)
        scroll = ttk.Scrollbar(right, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y'); self.table.pack(fill='both', expand=True)
        self.table.bind('<<TreeviewSelect>>', self.select_row)
        playback = ttk.Frame(root, padding=10); playback.pack(fill='x')
        for label, command in (('Play', self.play), ('Pause', self.pause)):
            ttk.Button(playback, text=label, command=command).pack(side='left')
        self.slider = tk.Scale(playback, from_=0, to=0, orient='horizontal', showvalue=True, command=self.scrub)
        self.slider.pack(side='left', fill='x', expand=True)
        self.left, self.right = tk.DoubleVar(value=0), tk.DoubleVar(value=0)
        for label, var in (('Left MODEL effort', self.left), ('Right MODEL effort', self.right)):
            frame = ttk.Frame(root, padding=(10, 3)); frame.pack(fill='x')
            ttk.Label(frame, text=label, width=22).pack(side='left')
            ttk.Progressbar(frame, variable=var, maximum=1000000).pack(side='left', fill='x', expand=True)
        self.details = tk.StringVar(value='No recording. Edit inputs, then Run entire simulation.')
        ttk.Label(root, textvariable=self.details, padding=10, wraplength=1140).pack(fill='x')
        self.status = tk.StringVar(value='No model run')
        ttk.Label(root, textvariable=self.status, padding=5).pack(fill='x')
        exports = ttk.Frame(root, padding=8); exports.pack(fill='x')
        for label, kind in (('Export HTML', 'html'), ('Export MODEL JSON', 'proof'), ('Export candidate', 'candidate'), ('Export wire input', 'wire')):
            ttk.Button(exports, text=label, command=lambda k=kind: self.export(k)).pack(side='left', padx=4)
        ttk.Label(exports, text='runtime_authorized=False | actual_virtual_output=None | physical_output=None').pack(side='right')
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.load_preset()

    def clear_display(self):
        self.pause()
        self.controller.invalidate()
        self.table.delete(*self.table.get_children())
        self.slider.configure(to=0); self.slider.set(0)
        self.left.set(0); self.right.set(0)
        self.details.set('No current recording; effort INHIBITED. Run the complete session explicitly.')

    def show_actions(self):
        value = json.loads(self.controller.session_bytes())
        self.actions.configure(state='normal'); self.actions.delete('1.0', 'end')
        for a in value['actions']:
            self.actions.insert('end', f"{a['at_us']:>8} {a['kind']} {a['id']}\n")
        self.actions.configure(state='disabled')
        self.duration.set(str(value['duration_us']))
        self.status.set(f"{len(value['actions'])} actions; edits do not replay. MODEL ONLY.")

    def error(self, error):
        self.status.set('BLOCKED: ' + str(error))
        messagebox.showerror('Studio input/report error — NO OUTPUT', str(error), parent=self.root)

    def load_preset(self):
        self.clear_display()
        try:
            self.controller.load(fixtures.session(self.preset.get())); self.show_actions()
        except (ValueError, TypeError, OSError) as error: self.error(error)

    def new_session(self):
        self.clear_display()
        try:
            self.controller.load(encode_session(dict(session_schema='BB_P226_STUDIO_ACTIONS_V1', session_id='manual', duration_us=int(self.duration.get()), actions=[])))
            self.show_actions()
        except (ValueError, TypeError) as error: self.error(error)

    def append(self):
        self.clear_display()
        try:
            value = json.loads(self.controller.session_bytes())
            value['duration_us'] = int(self.duration.get())
            self.controller.load(encode_session(value))
            a = dict(id='ui_' + str(len(value['actions']) + 1), kind=self.kind.get(), at_us=int(self.at.get()))
            if a['kind'] == 'CONTROL_VALID':
                a.update(flap_micro=self.flap.get(), steer_micro=self.steer.get(), arm_switch=self.arm.get())
            self.controller.append(a); self.show_actions()
        except (ValueError, TypeError, tk.TclError) as error: self.error(error)

    def replay(self):
        self.clear_display()
        self.status.set('Running complete offline model…'); self.root.update_idletasks()
        try:
            report = self.controller.run(**self.bindings)
            for i, row in enumerate(report.model_ticks):
                self.table.insert('', 'end', iid=str(i), values=(row.eval_at_us, row.model_state.value, row.rf_effective,
                    f'{row.model_effort_left_micro}/{row.model_effort_right_micro}'))
            self.slider.configure(to=max(0, len(report.model_ticks) - 1))
            self.status.set(report.outcome + '; ' + (report.diagnostic or 'NO OUTPUT'))
            self.render()
        except (ValueError, TypeError, OSError) as error: self.error(error)

    def render(self):
        row = self.controller.row
        if row is None: return
        self._updating = True; self.slider.set(self.controller.index); self._updating = False
        self.left.set(row.model_effort_left_micro or 0); self.right.set(row.model_effort_right_micro or 0)
        self.details.set(f'{row.eval_at_us} us | MODEL {row.model_state.value} | RF {row.rf_effective} | ARM request {row.arm_switch_requested} (NOT GRANTED)\n'
            f'L/R micro: {row.model_effort_left_micro}/{row.model_effort_right_micro} (None = INHIBITED); {row.model_input_mode}; '
            f'LOW qualified {row.model_snapshot.low_qualified_eval_us}; HIGH edge {row.model_snapshot.high_edge_at_us}\n'
            f'Reasons: {", ".join(row.model_reasons)} | D2: {", ".join(row.triage_reasons)}')

    def scrub(self, value):
        if self._updating or not self.controller.report or not self.controller.report.model_ticks: return
        self.controller.seek(int(value)); self.render()

    def select_row(self, event=None):
        selected = self.table.selection()
        if selected and self.controller.report:
            self.controller.seek(int(selected[0])); self.render()

    def play(self):
        self.controller.play()
        if self.timer is None: self.pulse()

    def pulse(self):
        self.timer = None
        if self.controller.playing:
            self.controller.step(); self.render()
            self.timer = self.root.after(100, self.pulse)

    def pause(self):
        self.controller.pause()
        if self.timer is not None:
            self.root.after_cancel(self.timer); self.timer = None

    def export(self, kind):
        try:
            report = self.controller.report
            if report is None or report.outcome != 'MODEL_REPLAY_COMPLETE':
                raise ValueError('Run a complete acknowledged model session before export')
            suffix = dict(html='.html', proof='.model.json', candidate='.model-candidate.jsonl', wire='.wire.json')[kind]
            path = filedialog.asksaveasfilename(parent=self.root, defaultextension=suffix, initialfile='offline-model' + suffix)
            if path: offline.export(report, kind, path)
        except (ValueError, TypeError, OSError) as error: self.error(error)

    def close(self):
        self.pause(); self.root.destroy()


def launch(case='nominal'):
    try:
        root = tk.Tk()
    except tk.TclError as error:
        raise ValueError('Tk display unavailable; use --case nominal --text') from error
    StudioWindow(root, case)
    root.mainloop()
    return 0
