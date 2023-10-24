local is_running = false

local REQ_ALLOC_ODT_ENTRY = string.char(0xD3)
local REQ_ALLOC_ODT = string.char(0xD4)
local REQ_ALLOC_DAQ = string.char(0xD5)
local REQ_FREE_DAQ = string.char(0xD6)
local REQ_START_STOP_SYNCH = string.char(0xDD)
local REQ_GET_STATUS = string.char(0xFD)
local REQ_CONNECT = string.char(0xFF)

local RES_ERR_DAQ_ACTIVE = string.char(0xFE, 0x11)

function payload_hook(request, current_response)
   if #request >= 1 then
      -- check the first byte of the request-payload, is it one of the
      -- commands we're interested in?
      cmd = request:sub(1, 1)
      if REQ_GET_STATUS == cmd then
         print "Lua: GET_STATUS received"
      elseif REQ_CONNECT == cmd then
         print "Lua: CONNECT received, resetting"
         is_running = false
      elseif REQ_START_STOP_SYNCH == cmd then
         print "Lua: START_STOP_SYNCH received"
         if is_running then
            is_running = false
            print " * stopped"
         else
            is_running = true
            print " * started"
         end
      elseif REQ_ALLOC_ODT_ENTRY == cmd then
         print "Lua: ALLOC_ODT_ENTRY received"
      elseif REQ_ALLOC_ODT == cmd then
         print "Lua: ALLOC_ODT received"
      elseif REQ_ALLOC_DAQ == cmd then
         print "Lua: ALLOC_DAQ received"
      elseif REQ_FREE_DAQ == cmd then
         print "Lua: FREE_DAQ received"
         if false == is_running then
            print " * Measurement is stopped -- OK"
         else
            print " * Measurement is running -- FAILURE"
            -- change the response
            return true, RES_ERR_DAQ_ACTIVE
         end
      end
   end
end
