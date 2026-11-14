"""Design/196 demo alias for the same integrated Studio CLI."""
try:
    from .studio import main
except ImportError:
    from studio import main

if __name__ == '__main__':
    raise SystemExit(main())
