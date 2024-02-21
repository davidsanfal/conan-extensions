import json
import os
import argparse
from conan.cli.commands.export import common_args_export
from conan.cli.command import OnceArgument
from conan.api.conan_api import ConanAPI, ConfigAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command, conan_subcommand


def dir_path(arg_path):
    if os.path.isdir(arg_path):
        return arg_path
    else:
        raise argparse.ArgumentTypeError(f"{arg_path} is not a valid path")


@conan_subcommand()
def create_ssh(conan_api, parser, subparser, *args):
    """
    run Conan using SSH
    """


@conan_subcommand()
def create_docker(conan_api, parser, subparser, *args):
    """
    run conan inside a Docker continer
    """
    # import docker only if needed
    import docker
    home = ConfigAPI(conan_api).home()
    #
    subparser.add_argument('path', type=dir_path, help='conan create path arg')
    # PROFILE dockerfile docker:path
    subparser.add_argument('--dockerfile', nargs='?', default=os.path.join(home, 'extensions/commands/remote/'), type=dir_path, help=f'dockerfile absolute directory path. Default: {os.path.join(home, "extensions/commands/remote/")}')
    # PROFILE dockerfile docker:image
    subparser.add_argument('-i', '--image', nargs='?', default='conanremote', help='docker image name. Default: conanremote')
    # DRY RUN MODE: Shows what you are going to run inside the container and return.
    subparser.add_argument('--dry-run', action='store_true', default=False, help='DEBUG MODE. Shows what you are going to run')

    args, extra_args = parser.parse_known_args(*args)

    # CACHE copy and restore
    volumes={
        home: {'bind': '/root/.conan2', 'mode': 'rw'},
        args.path: {'bind': args.path, 'mode': 'rw'}
    }

    # RECREATE CONAN COMMAND: https://docs.conan.io/2/devops/save_restore.html
    command = " ".join(['conan create', args.path] + extra_args)

    # DRY RUN MODE: Shows what you are going to run and return.
    if args.dry_run:
        ConanOutput().info(msg=f'\nDOCKER COMMAND: {command}')
        ConanOutput().info(msg=f'\nVOLUMES: {json.dumps(volumes, indent=4)}')
        return

    # Init docker python api
    docker_client = docker.from_env()

    # Create image and run the container
    if args.dockerfile:
        docker_client.images.build(path=args.dockerfile, tag=args.image)
    container = docker_client.containers.run( args.image, command, volumes=volumes, detach=True)

    # Realtime logs
    output = container.attach(stdout=True, stream=True, logs=True)
    for line in output:
        ConanOutput().info(msg=line.decode('utf-8', errors='ignore'))

    # Clean docker
    container.wait()
    container.stop()
    container.remove()


@conan_subcommand()
def create_k8s(conan_api, parser, subparser, *args):
    """
    run Conan inside a k8s pod
    """


@conan_command(group="Custom commands")
def create(conan_api: ConanAPI, parser, *args):
    """
    run Conan remotelly
    """
