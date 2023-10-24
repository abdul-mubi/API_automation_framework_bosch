-- DeleteCANFrame.lua
-- This script deletes the CAN frame at the last position of the list
-- of frames to be transmitted.

--hook execution counter
local count = 0

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if count > 1000 then
		--delete last CAN frame
		lastEntry = #CANFrames
		table.remove(CANFrames, lastEntry)
		--or CANFrames[#CANFrames] = nil
	end
	
	--return modified CANFrames
	return CANFrames
end