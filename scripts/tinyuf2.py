Import("env")

from SCons.Script import COMMAND_LINE_TARGETS

import os
import shutil
import sys
import shlex
import subprocess

project_dir = env["PROJECT_DIR"]
pioenv = env["PIOENV"]
config = env.GetProjectConfig()
section = f"env:{pioenv}"
board_override = ""
if config.has_option(section, "custom_tinyuf2_board"):
    board_override = config.get(section, "custom_tinyuf2_board")

try:
    FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-espidf")
except Exception:
    FRAMEWORK_DIR = ""

board_name = board_override or pioenv
serial_port = env.GetProjectOption("upload_port", "")
try:
    upload_speed = env.GetProjectOption("upload_speed")
except KeyError:
    upload_speed = ""

if not board_name:
    raise RuntimeError("tinyuf2_board option is required for this environment")

idf_env_template = env["ENV"].copy()

# Resolve build directory per board to keep outputs separated.
build_dir = os.path.join(project_dir, "build", board_name)
os.makedirs(build_dir, exist_ok=True)

board_sdkconfig = os.path.join(project_dir, "ports", "espressif", "boards", board_name, "sdkconfig")
root_sdkconfig = os.path.join(project_dir, f"sdkconfig.{board_name}")

if os.path.isfile(board_sdkconfig) and not os.path.isfile(root_sdkconfig):
    shutil.copy(board_sdkconfig, root_sdkconfig)

_skip_alias = env.Alias("tinyuf2-skip", None)
env.AlwaysBuild(_skip_alias)


def _resolve_idf_command():
    python_exe = env.subst("$PYTHONEXE")
    if not python_exe or python_exe == "$PYTHONEXE":
        python_exe = sys.executable

    idf_python_env = env.subst("$IDF_PYTHON_ENV_PATH")
    if not idf_python_env or idf_python_env == "$IDF_PYTHON_ENV_PATH":
        default_env_root = os.path.expanduser("~/.espressif/python_env")
        if os.path.isdir(default_env_root):
            env_dirs = sorted(
                (os.path.join(default_env_root, d) for d in os.listdir(default_env_root)),
                key=os.path.getmtime,
                reverse=True,
            )
            for candidate in env_dirs:
                python_candidate = os.path.join(candidate, "bin", "python")
                if os.path.isfile(python_candidate):
                    idf_python_env = candidate
                    break

    idf_py_cmd = env.subst("$IDF_PY")

    if idf_python_env and (not python_exe or python_exe == sys.executable):
        python_candidate = os.path.join(idf_python_env, "bin", "python")
        if os.path.isfile(python_candidate):
            python_exe = python_candidate

    print("[tinyuf2] PYTHONEXE:", python_exe, flush=True)
    print("[tinyuf2] IDF_PYTHON_ENV_PATH:", idf_python_env, flush=True)
    print("[tinyuf2] IDF_PY:", idf_py_cmd, flush=True)

    idf_py_value = env.subst("$IDF_PY")
    if idf_py_value and idf_py_value != "$IDF_PY":
        parts = shlex.split(idf_py_value)
        if parts and parts[0].endswith(".py"):
            return [python_exe] + parts
        return parts

    candidates = []

    idf_path = env.subst("$IDF_PATH")
    if idf_path and idf_path != "$IDF_PATH":
        candidates.append(os.path.join(idf_path, "tools", "idf.py"))
        candidates.append(os.path.join(idf_path, "idf.py"))

    if FRAMEWORK_DIR:
        candidates.append(os.path.join(FRAMEWORK_DIR, "tools", "idf.py"))
        candidates.append(os.path.join(FRAMEWORK_DIR, "idf.py"))

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return [python_exe, candidate]

    which_idf = shutil.which("idf.py")
    if which_idf:
        if which_idf.endswith(".py"):
            return [python_exe, which_idf]
        return [which_idf]

    raise RuntimeError("Unable to resolve idf.py path from PlatformIO configuration")


def _call_idf(arguments):
    cmd = _resolve_idf_command()
    cmd += ["-B", build_dir]

    cmd.append(f"-DBOARD={board_name}")
    cmd.append(f"-DIDF_BOARD={board_name}")

    if serial_port:
        cmd.extend(["-p", serial_port])

    if upload_speed:
        cmd.extend(["-b", str(upload_speed)])

    cmd += list(arguments)

    # Echo the invoked command when PlatformIO runs in verbose mode.
    cmd_display = " ".join(cmd)
    print("[tinyuf2] command:", cmd_display, flush=True)
    call_env = idf_env_template.copy()
    call_env["BOARD"] = board_name
    call_env["IDF_BOARD"] = board_name

    extra_args = call_env.get("IDF_EXTRA_CMAKE_ARGS", "").strip()
    filtered_args = []
    if extra_args:
        for token in extra_args.split():
            if token.startswith("-DTINYUF2_PLATFORMIO_SKIP"):
                continue
            filtered_args.append(token)
    board_args = [f"-DBOARD={board_name}", f"-DIDF_BOARD={board_name}"]
    if filtered_args:
        board_args = filtered_args + board_args
    call_env["IDF_EXTRA_CMAKE_ARGS"] = " ".join(board_args)

    if FRAMEWORK_DIR:
        tools_path = os.path.join(FRAMEWORK_DIR, "tools")
        current_pythonpath = call_env.get("PYTHONPATH", "")
        if tools_path not in current_pythonpath.split(os.pathsep):
            call_env["PYTHONPATH"] = (
                (current_pythonpath + os.pathsep if current_pythonpath else "")
                + tools_path
            )

    print("[tinyuf2] env BOARD:", call_env.get("BOARD"), flush=True)
    print("[tinyuf2] env IDF_EXTRA_CMAKE_ARGS:", call_env.get("IDF_EXTRA_CMAKE_ARGS"), flush=True)
    print("[tinyuf2] env PYTHONPATH:", call_env.get("PYTHONPATH"), flush=True)

    with open(os.path.join(build_dir, "idf_invocations.log"), "a", encoding="utf-8") as _idf_log:
        _idf_log.write(cmd_display + "\n")

    if serial_port:
        call_env.setdefault("ESPTOOL_PORT", serial_port)

    if upload_speed:
        call_env.setdefault("ESPTOOL_BAUD", str(upload_speed))

    subprocess.check_call(cmd, cwd=project_dir, env=call_env)


def _skip_default_build(env):
    print("[tinyuf2] Skipping default PlatformIO build step")
    return _skip_alias


env.AddMethod(_skip_default_build, "BuildProgram")


def _build_action(target, source, env):
    _call_idf(["build"])
    return None


def _clean_action(target, source, env):
    _call_idf(["fullclean"])
    return None


def _flash_action(target, source, env):
    _call_idf(["flash"])
    return None

build_description = f"Build TinyUF2 for {board_name}"
clean_description = f"Clean TinyUF2 build for {board_name}"
flash_description = f"Flash TinyUF2 to {serial_port or 'default port'}"

build_action = env.Action(_build_action, build_description)
clean_action = env.Action(_clean_action, clean_description)
flash_action = env.Action(_flash_action, flash_description)

env.AddCustomTarget(
    name="tinyuf2",
    dependencies=None,
    actions=[build_action],
    title=build_description,
    description="Invoke idf.py to build the TinyUF2 bootloader",
)

env.AddCustomTarget(
    name="tinyuf2-clean",
    dependencies=None,
    actions=[clean_action],
    title=clean_description,
    description="Invoke idf.py fullclean for the TinyUF2 bootloader",
)

env.AddCustomTarget(
    name="tinyuf2-flash",
    dependencies=None,
    actions=[flash_action],
    title=flash_description,
    description="Invoke idf.py flash for the TinyUF2 bootloader",
)

_KNOWN_TARGETS = {
    "tinyuf2": ["build"],
    "tinyuf2-clean": ["fullclean"],
    "tinyuf2-flash": ["flash"],
}

requested_targets = list(COMMAND_LINE_TARGETS)
print("[tinyuf2] requested targets:", requested_targets, flush=True)
with open(os.path.join(build_dir, "pio_targets.log"), "a", encoding="utf-8") as _log_file:
    _log_file.write(",".join(requested_targets) + "\n")
if not requested_targets:
    _call_idf(["build"])
    env.Exit(0)

if requested_targets and set(requested_targets).issubset(_KNOWN_TARGETS):
    for target_name in requested_targets:
        for argument in _KNOWN_TARGETS[target_name]:
            _call_idf([argument])
    env.Exit(0)
