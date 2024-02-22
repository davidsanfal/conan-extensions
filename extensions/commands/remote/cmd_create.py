import json
import os
import argparse
import shutil
from conan.cli.commands.export import common_args_export
from conan.cli.command import OnceArgument
from conan.api.conan_api import ConanAPI, ConfigAPI
from conan.api.output import ConanOutput
from conan.cli.command import conan_command, conan_subcommand
from conan.api.model import ListPattern


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
    subparser.add_argument('path', type=dir_path, help='conan create path arg')
    subparser.add_argument('--dockerfile',
                           nargs='?',
                           default=os.path.join(home, 'extensions/commands/remote/'),
                           type=dir_path,
                           help=f'dockerfile absolute directory path. Default: {os.path.join(home, "extensions/commands/remote/")}')
    subparser.add_argument('-i', '--image', nargs='?', default='conanremote', help='docker image name. Default: conanremote')
    subparser.add_argument('--dry-run', action='store_true', default=False, help='DEBUG MODE. Shows what you are going to run')

    args, extra_args = parser.parse_known_args(*args)

    remote_home = os.path.join(args.path, '.conanremote')
    tgz_path = os.path.join(remote_home, 'conan_cache_save.tgz')
    volumes = {
        args.path: {'bind': args.path, 'mode': 'rw'}
    }

    environment = {
        'CONAN_REMOTE_WS': args.path,
        'CONAN_REMOTE_COMMAND': ' '.join(['conan create', args.path] + extra_args)
    }

    # DRY RUN MODE: Shows what you are going to run and return.
    if args.dry_run:
        ConanOutput().info(msg=f'\nVOLUMES: {json.dumps(volumes, indent=4)}')
        ConanOutput().info(msg=f'\nENVIRONMENT: {json.dumps(environment, indent=4)}')
        return


    # CREATE CONAN REMOTE FILES
    shutil.rmtree(remote_home, ignore_errors=True)
    os.mkdir(remote_home)
    conan_api.cache.save(conan_api.list.select(ListPattern("*")), tgz_path)
    shutil.copytree(os.path.join(home, 'profiles'), os.path.join(remote_home, 'profiles'))

    # Init docker python api
    docker_client = docker.from_env()

    # Create image and run the container
    if args.dockerfile:
        ConanOutput().info(msg=f'\nBuilding the Docker image: {args.image}')
        docker_client.images.build(path=args.dockerfile, tag=args.image)
    ConanOutput().info(msg=f'\Running the Docker container\n')
    container = docker_client.containers.run(args.image,
                                             '/root/.conan2/conan-remote-init.sh',
                                             volumes=volumes,
                                             environment=environment,
                                             detach=True)

    # Realtime logs
    output = container.attach(stdout=True, stream=True, logs=True)
    for line in output:
        ConanOutput().info(msg=line.decode('utf-8', errors='ignore'))

    # Clean docker
    container.wait()
    container.stop()
    container.remove()
    tgz_path = os.path.join(remote_home, 'conan_cache_docker.tgz')
    ConanOutput().info(f'New cache path: {tgz_path}')
    package_list = conan_api.cache.restore(tgz_path)


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
