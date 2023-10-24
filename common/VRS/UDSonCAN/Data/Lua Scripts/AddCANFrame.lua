-- AddCANFrame.lua
-- This script adds a new CAN frame to the list of frames to be transmitted.
-- The new CAN frame is inserted at the last position of the list.

--hook execution counter
local count = 0

local newCANFrame = {frameID = 0x720, payload = {0x12, 0x21, 0x82, 0x2A, 0x18, 0x04, 0x7F, 0xB6}}

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if count > 1000 then
		--add new CAN frame
		table.insert(CANFrames, newCANFrame)
	end
	
	--return modified CANFrames
	return CANFrames
end