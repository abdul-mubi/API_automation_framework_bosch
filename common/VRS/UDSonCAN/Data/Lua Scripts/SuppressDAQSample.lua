-- SuppressDAQSample.lua
-- This script suppresses all CAN frames from being sent.

--hook execution counter
local count = 0

function FreeRunningHook(CANFrames)

	--increment counter for each hook call
	count = count + 1
	
	if (count > 1000) then
		--suppress all CAN Frames
		return {}
	end
	
	return CANFrames
end