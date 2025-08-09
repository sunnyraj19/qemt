
import argparse, sys, runpy

def main():
    parser = argparse.ArgumentParser(description='QEMT CLI')
    sub = parser.add_subparsers(dest='cmd')

    runp = sub.add_parser('run', help='Run an experiment')
    runp.add_argument('--exp', required=True, choices=['grover_zne', 'vqe_opt', 'qaoa_dd'], help='Experiment to run')

    args = parser.parse_args()

    if args.cmd == 'run':
        if args.exp == 'grover_zne':
            runpy.run_module(mod_name='experiments.01_grover_zne', run_name='__main__')
        elif args.exp == 'vqe_opt':
            runpy.run_module(mod_name='experiments.02_vqe_h2_opt', run_name='__main__')
        elif args.exp == 'qaoa_dd':
            runpy.run_module(mod_name='experiments.03_qaoa_maxcut_dd', run_name='__main__')
        else:
            print('Unknown experiment', file=sys.stderr); sys.exit(2)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
