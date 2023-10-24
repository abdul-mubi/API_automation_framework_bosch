XCP "Seed and Key" DLLs
=======================

Source Code
-----------

The source code is within the VRS repository. This is a self-contained
sub-project without dependencies. Look below "Tools/SeedAndKey".

Binaries
--------

Each of the folders contains a DLL for the respective
architecture. Deploy as needed.

Specialities
------------

"SeedNKeyXcp_Wrong.dll" is a 32-bit Windows DLL that always generates
wrong keys. No equivalent DLL is provided for other platforms.

Usage
-----

Configure the VRS to require the use of the Seed & Key mechanism:

p_XcpResourceProtect_u8 = 29
p_XcpSeedLength_u8 = 255
p_XcpKeyLength_u8 = 255

... and use an A2L file with corresponding information.
