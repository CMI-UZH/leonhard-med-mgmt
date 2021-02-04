#! python

import argparse
import os
import subprocess

cmd_str = '''

def_file_path='{def_file}'
build_dir='$HOME/temp/'

# Open ssh tunnel for the subsequent commands (might need to increase sleep time)
ssh -f -o ExitOnForwardFailure=yes ohdsi sleep {wait_time}

# Transfer the edited specification file to OHDSI instance (notice -R)
lftp sftp://{build_machine} -e "mirror -R -P 12 --use-pget-n=1 $def_file_path $build_dir; exit"

# Run 'singularity build' on OHDSI
ssh {build_machine} "cd $build_dir; specfile=\$(ls -t *.spec | head -n1 | sed 's/\.[^.]*$//'); sudo singularity build \$specfile.sif \$specfile.spec"

# Copy the new image back to LeoMed
lftp sftp://{build_machine} -e "mirror -P 12 --use-pget-n=1 $build_dir $def_file_path; exit"

'''

epilog_str = '''
Example for connecting to LeoMed:
    build_image --def_file image.sif --build_machine ohdsi --wait_time 360\n

'''


def build_image(def_file, build_machine, wait_time, ):
    # clean up slashes
    def_file = os.path.join(def_file, '')

    cmd = cmd_str.format(def_file=def_file, build_machine=build_machine, wait_time=wait_time)
    subprocess.call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_str)
    parser.add_argument('--def_file', help='the local code directory you want to sync', required=True)
    parser.add_argument('--build_machine', help='the ssh config key for the machine you want to build the image on', required=True)
    parser.add_argument('--wait_time', type=int, help='the length of time the ssh connection stays open',
                        required=False, default=120)
    args = parser.parse_args()

    build_image(def_file=args.def_file, build_machine=args.build_machine, wait_time=args.wait_time)


if __name__ == '__main__':
    main()
