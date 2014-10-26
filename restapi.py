from bottle import Bottle, run, request
import uuid, os

from winservice import Service, instart
import constants
import netutilsv2
import vmutilsv2
import vhdutilsv2
import rdputilsv2

IMAGE_PATH = "I:\\images"
DEFAULT_IMAGE = "48e66e4d9a1745f2957ed6d9a0b74d51"
VSWITCH_NAME = "extend"

app = Bottle()
net = netutilsv2.HyperVUtilsV2R2()
vhd = vhdutilsv2.VHDUtilsV2()
vm = vmutilsv2.VMUtilsV2()
rdp = rdputilsv2.RDPConsoleUtilsV2()

@app.route("/instances")
def list_vm():
    return {"vms" : vm.list_instances()}

@app.route("/instances/<vm_name>")
def show_vm(vm_name):
    info = vm.get_vm_summary_info(vm_name)
    cpu_info = vm.get_processor_load_percentage(vm_name=vm_name)
    vm_id = vm.get_vm_id(vm_name)
    info["cpu"] = cpu_info.get(vm_id, 0)
    return info

@app.route("/instances/<vm_name>/suspend", method="POST")
def suspend_vm(vm_name):
    vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_SUSPENDED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/resume", method="POST")
def resume_vm(vm_name):
    vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_ENABLED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/pause", method="POST")
def suspend_vm(vm_name):
    vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_PAUSED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/unpause", method="POST")
def unpause_vm(vm_name):
    vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_ENABLED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/poweron", method="POST")
def poweron_vm(vm_name):
    vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_ENABLED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/poweroff", method="POST")
def poweroff_vm(vm_name):
    if(request.json["hard"]):
        vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_DISABLED)
    else:
        vm.soft_shutdown_vm(vm_name)
    return {"result": "success"}

@app.route("/instances/<vm_name>/reboot", method="POST")
def reboot_vm(vm_name):
    if(request.json['hard']):
        print "hard reboot"
        vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_REBOOT)
    else:
        vm.soft_shutdown_vm(vm_name)
        vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_ENABLED)
    return {"result": "success"}

@app.route("/instances/<vm_name>/console")
def get_rdp_console(vm_name):
    vm_id = vm.get_vm_id(vm_name)
    port = rdp.get_rdp_console_port()
    cmd = "wfreerdp.exe /vmconnect:%s /v:<host_ip>:%s" % (vm_id, port)
    return {"rdp_console": cmd}

@app.route("/images")
def get_images():
    images = os.listdir(os.path.join(IMAGE_PATH, "_base"))
    return {"images": images}

@app.route("/instances/<vm_name>", method="DELETE")
def destroy_vm(vm_name):
    if(vm.vm_exists(vm_name)):
        vm.set_vm_state(vm_name, constants.HYPERV_VM_STATE_DISABLED)
        (file_path, vol) = vm.get_vm_storage_paths(vm_name)
        for f in file_path:
            os.unlink(f)
        vm.destroy_vm(vm_name)
    return {"result": "success"}

@app.route("/instances", method="POST")
def create_vm():
    body = request.json
    name = body.get("name", uuid.uuid4().__str__())
    cpu = body.get("cpu", 1)
    mem = body.get("mem", 512)
    vhd_ext = body.get("vhdext", None)
    image = body.get("image", DEFAULT_IMAGE)
    root_image = uuid.uuid4().get_hex()
    base_image_path = os.path.join(IMAGE_PATH, "_base", "%s.vhd" % image)
    root_image_path = os.path.join(IMAGE_PATH, "%s.vhd" % root_image)
    ext_vhd_path = None
    if(vhd_ext):
        vhd_ext = int(vhd_ext)
        ext_vhd_path = os.path.join(IMAGE_PATH, "%s_ext_%d.%s" % (root_image, vhd_ext,
                                                                  vhd.get_best_supported_vhd_format()))
    vm.create_vm(name, mem, cpu, False, 1.0)
    vhd.create_differencing_vhd(root_image_path, base_image_path)
    if(vhd_ext and ext_vhd_path):
        print ext_vhd_path
        print vhd_ext
        print vhd.get_best_supported_vhd_format()
        vhd.create_dynamic_vhd(ext_vhd_path, vhd_ext * (1024**3), vhd.get_best_supported_vhd_format())

    vm.attach_ide_drive(name, root_image_path, 0, 0, constants.IDE_DISK)
    if(vhd_ext and ext_vhd_path):
        vm.attach_ide_drive(name, ext_vhd_path, 0, 1, constants.IDE_DISK)
    nic_name = uuid.uuid4().get_hex()
    vm.create_nic(name, nic_name)
    net.connect_vnic_to_vswitch(VSWITCH_NAME, nic_name)

    vm.set_vm_state(name, constants.HYPERV_VM_STATE_ENABLED)
    return {"name":name,
            "cpu":cpu,
            "mem":mem,
            "disk":{"root": root_image_path, "ext": ext_vhd_path},
            "nic": nic_name}




class BottleServer(Service):
    def start(self):
        run(app, host='0.0.0.0', port=8080)

    def stop(self):
        pass

instart(BottleServer, 'bottleServer', 'bottleServer')