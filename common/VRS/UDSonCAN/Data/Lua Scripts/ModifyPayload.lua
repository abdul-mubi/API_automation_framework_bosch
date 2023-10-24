-- ModifyPayload.lua
-- This script modifies the signal data of a CAN frame with ID 0x690.
-- The PID is unmodified.

--hook execution counter
local count = 0

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if count > 1000 then
		--iterate through each CAN frame until frame ID 0x690 is found
		for i, CANFrame in ipairs(CANFrames) do
			if CANFrame.frameID == 0x690 then
				--modify payload except PID
				newPayload = {CANFrame.payload[1], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}
				CANFrame.payload = newPayload
			end
		end
	end
	
	--return modified CANFrames
	return CANFrames
end