import xml.dom.minidom
from re import sub
from logilabvm.lib import show, create
from logilabvm.lib.test import init, clear
import unittest

class TestCreate(unittest.TestCase):
    def setUp(self):
        clear.run()
        #init.run()

    def tearDown(self):
        clear.run()

    def testTypeQemu(self):
        cmp = """
        <domain type="qemu">
         <name>qemuvm</name>
         <memory>256000</memory>
         <vcpu>2</vcpu>
         <clock sync="utc"/>
         <features><acpi/></features>
         <os>
          <boot dev="hd"/>
          <type arch="i686" machine="pc">hvm</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <emulator>/usr/bin/qemu</emulator>
          <disk device="disk" type="file">
           <source file="toto"/>
           <target dev="hda"/>
          </disk>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","qemu","--sys","name=qemuvm,mem=256000,vcpu=2,boot=hd","--dev","file=toto,device=disk,target=hda"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testTypeKVM(self):
        cmp = """
        <domain type="kvm">
         <name>kvmvm</name>
         <memory>512000</memory>
         <vcpu>4</vcpu>
         <clock sync="utc"/>
         <features><acpi/></features>
         <os>
          <boot dev="cdrom"/>
          <type arch="i686" machine="pc">hvm</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <emulator>/usr/bin/kvm</emulator>
          <disk device="cdrom" type="file">
           <source file="bibi"/>
           <target dev="sda"/>
          </disk>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","kvm","--sys","name=kvmvm,mem=512000,vcpu=4,boot=cdrom","--dev","file=bibi,device=cdrom,target=sda"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testTypeOpenVZ(self):
        cmp = """
        <domain type="openvz">
         <name>101</name>
         <memory>128000</memory>
         <vcpu>1</vcpu>
         <clock sync="utc"/>
         <os>
          <init>/sbin/init</init>
          <type arch="i686" machine="pc">exe</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <filesystem type="template">
           <source name="debian-4.0-x86"/>
           <target dir="/"/>
          </filesystem>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","openvz","--sys","name=101,mem=128000,vcpu=1,ostemplate=debian-4.0-x86,host=101,domain=unittest.com","--dev","template=debian-4.0-x86"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testTwoDev(self):
        cmp = """
        <domain type="kvm">
         <name>kvmvm</name>
         <memory>512000</memory>
         <vcpu>4</vcpu>
         <clock sync="utc"/>
         <features><acpi/></features>
         <os>
          <boot dev="cdrom"/>
          <type arch="i686" machine="pc">hvm</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <emulator>/usr/bin/kvm</emulator>
          <disk device="disk" type="file">
           <source file="myimg"/>
           <target dev="sda"/>
          </disk>
          <disk device="cdrom" type="file">
           <source file="myiso"/>
           <target dev="sdb"/>
          </disk>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","kvm","--sys","name=kvmvm,mem=512000,vcpu=4,boot=cdrom","--dev","file=myimg,device=disk,target=sda","--dev","file=myiso,device=cdrom,target=sdb"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testOneNet(self):
        cmp = """
        <domain type="openvz">
         <name>101</name>
         <memory>128000</memory>
         <vcpu>1</vcpu>
         <clock sync="utc"/>
         <os>
          <init>/sbin/init</init>
          <type arch="i686" machine="pc">exe</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <filesystem type="template">
           <source name="debian-4.0-x86"/>
           <target dir="/"/>
          </filesystem>
          <interface type="bridge">
           <target dev="vnet0"/>
           <mac address="11:22:33:44:55:66"/>
           <source bridge="br0"/>
          </interface>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","openvz","--sys","name=101,mem=128000,vcpu=1,ostemplate=debian-4.0-x86,host=101,domain=unittest.com","--dev","template=debian-4.0-x86","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testTwoNet(self):
        cmp = """
        <domain type="openvz">
         <name>101</name>
         <memory>128000</memory>
         <vcpu>1</vcpu>
         <clock sync="utc"/>
         <os>
          <init>/sbin/init</init>
          <type arch="i686" machine="pc">exe</type>
         </os>
         <on_poweroff>destroy</on_poweroff>
         <on_reboot>restart</on_reboot>
         <on_crash>restart</on_crash>
         <devices>
          <filesystem type="template">
           <source name="debian-4.0-x86"/>
           <target dir="/"/>
          </filesystem>
          <interface type="bridge">
           <target dev="vnet0"/>
           <mac address="11:22:33:44:55:66"/>
           <source bridge="br0"/>
          </interface>
          <interface type="user">
           <mac address="66:55:44:33:22:11"/>
          </interface>
         </devices>
        </domain>"""
        doc1 = xml.dom.minidom.parseString(cmp)
        filename = create.run(["--type","openvz","--sys","name=101,mem=128000,vcpu=1,ostemplate=debian-4.0-x86,host=101,domain=unittest.com","--dev","template=debian-4.0-x86","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0","--net","method=user,mac=66:55:44:33:22:11,mac_int=66:55:44:33:22:12"])[1]
        doc2 = xml.dom.minidom.parse(filename)
        tree1 = sub("\s*\n\s*", "", doc1.toxml())
        tree2 = sub("\s*\n\s*", "", doc2.toxml())
        self.assertTrue(tree1 == tree2)

    def testAttributeError(self):
        args = ["--sys","name=101,mem=128000,vcpu=1","--dev","template=debian-4.0-x86","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"]
        self.assertRaises(AttributeError, create.run, args)
        args = ["--type","openvz","--sys","mem=128000,vcpu=1","--dev","template=debian-4.0-x86","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"]
        self.assertRaises(AttributeError, create.run, args)
        args = ["--type","openvz","--sys","name=101,vcpu=1","--dev","template=debian-4.0-x86","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"]
        self.assertRaises(AttributeError, create.run, args)
        args = ["--type","openvz","--sys","name=101,mem=128000","--net","method=bridge,mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"]
        self.assertRaises(AttributeError, create.run, args)
        args = ["--type","openvz","--sys","name=101,mem=128000,vcpu=1","--dev","template=debian-4.0-x86","--net","mac=11:22:33:44:55:66,bridge=br0,interface=vnet0"]
        self.assertRaises(AttributeError, create.run, args)

    def testRollback(self):
        pass

if __name__ == "__main__":
    unittest.main()
