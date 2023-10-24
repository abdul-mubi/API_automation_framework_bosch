-- ModifyPID.lua
-- This script modifies the PID of a CAN frame with ID 0x690.

--hook execution counter
local count = 0

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if count == 1000 then
		--iterate through each CAN frame until frame ID 0x690 is found
		for i, CANFrame in ipairs(CANFrames) do
			if CANFrame.frameID == 0x690 then
				--modify PID
				CANFrame.payload[1] = 0xFF
			end
		end
	end
	
	--return modified CANFrames
	return CANFrames
end