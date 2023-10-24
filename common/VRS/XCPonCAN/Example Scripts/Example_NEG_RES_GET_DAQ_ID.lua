-- define default response (empty)
local RES_EMPTY = ""
-- define CMD Request string
local REQ_GET_DAQ_ID = string.char(0xF2,0xFE,0x00,0x00,0x00,0x00,0x00,0x00)
-- define CMD Response string
local RES_GET_DAQ_ID = string.char(0xFE,0x20)

function payload_hook(request, current_response)
  -- default: do not change the response
  new_response = RES_EMPTY

  -- only do something
  --  * if the current request can be the one we're interested in (is long
  --    enough AND
  --  * the current response is there (at least two bytes are needed)
  if #request >= #REQ_GET_DAQ_ID and #current_response > 2 then
    -- enable for debugging: print(string.format("REQUEST: %u -- %02x %02x", #request, request:byte(1), request:byte(2)))
    -- check if the required command pattern is the prefix of the request
    if request:sub(1, #REQ_GET_DAQ_ID) == REQ_GET_DAQ_ID then
      print("GET_DAQ_ID detected, overwriting response")
      -- replace currently response unchanged response with the "rejection"
      new_response = RES_GET_DAQ_ID
    end
  end
  return new_response
end

-- check Priming run is done
io.write("#Payload_Hook::Priming run\n")
