--[[
Polling_UINT16.lua
Version: 0.1

Purpose: 
-----------
With this script it's possible to define the values of a single UINT16 variable
measured via XCPonCAN. 

Preconditions: 
----------------
- Only one label is configured in XCP for measurement. 
- The label has the format unsigned integer and size 16 bit
- The measurement is configured to "polling mode"

Use:
-------
Put the list of desired values in the array "DATAROW". 
The values will be returned one by one with each mesaurement request. At the end, 
it starts right from the beginning again. 

]]



local counter = 1
local SHORT_UPLOAD = 244
-- DATAROW provide the list of values of the measurement label. 
-- Each measurement increments the index by 1. At the end of the list, the index
-- is reset to the start of the list. 
DATAROW = {1,1,2,3,4,5,6,7,8,10,20,30,8,7,6,5,4,3,2,1}
--DATAROW = {0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.4,2.7,3,3.3,3.6,3.9,4.2,4.5,4.8,5.1,4.1,3.1,2.1,1.1,0.1}

function payload_hook (request, current_response)

  --print (request:byte (1))
  --print (current_response:byte (1, current_response:len()))
  
  if request:byte (1) == SHORT_UPLOAD then
    data_high = math.floor (DATAROW[counter]/256)
	data_low  = DATAROW[counter] - data_high
    myresponse = string.format ("%c%c%c", 255, data_low, data_high)
	counter = counter + 1
	if counter > #DATAROW then
	   counter = 1   
	end
    return true, myresponse
  end
  
  
end



