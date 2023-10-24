-- UnorderedPIDs.lua
-- This script modifies the order of the list of CAN frames to
-- be transmitted.

--hook execution counter
local count = 0

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if (count > 1000) and (#CANFrames >= 3) then
		--change order of PIDs
		reorderedCANFrames = {CANFrames[2], CANFrames[3], CANFrames[1]}
		--return reordered CANFrames
		return reorderedCANFrames
	end
	
	return CANFrames
end