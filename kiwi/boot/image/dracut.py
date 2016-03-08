# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import os

# project
from ...system.prepare import SystemPrepare
from ...compress import Compress
from ...logger import log
from ...command import Command
from ...system.kernel import Kernel
from .base import BootImageBase


class BootImageDracut(BootImageBase):
    """
        Implements preparation and creation of kiwi boot(initrd) images
        The kiwi initrd is a customized first boot initrd which allows
        to control the first boot an appliance. The kiwi initrd replaces
        itself after first boot by the result of dracut.
    """
    def prepare(self):
        """
            prepare new root system suitable to create an initrd from it
        """
        self.load_boot_xml_description()
        self.import_system_description_elements()

        log.info('Preparing boot image')
        system = SystemPrepare(
            xml_state=self.boot_xml_state,
            root_dir=self.boot_root_directory,
            allow_existing=True
        )
        manager = system.setup_repositories()
        system.install_bootstrap(
            manager
        )
        system.install_system(
            manager
        )

    def create_initrd(self, mbrid=None):
        if self.is_prepared():
            log.info('Creating generic dracut initrd archive')
            kernel_info = Kernel(self.boot_root_directory)
            kernel_version = kernel_info.get_kernel().version
            Command.run(
                [
                    'chroot', self.boot_root_directory,
                    'dracut', '--force',
                    '--no-hostonly',
                    '--no-hostonly-cmdline',
                    '--no-compress',
                    os.path.basename(self.initrd_file_name),
                    kernel_version
                ]
            )
            Command.run(
                [
                    'mv',
                    self.boot_root_directory + '/' + os.path.basename(
                        self.initrd_file_name
                    ),
                    self.initrd_file_name
                ]
            )
            log.info(
                '--> xz compressing archive'
            )
            compress = Compress(self.initrd_file_name)
            compress.xz()
            self.initrd_filename = compress.compressed_filename
