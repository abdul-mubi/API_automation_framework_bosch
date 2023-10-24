local REQ_PROGRAM_CLEAR = string.char(0xD1)
function payload_hook(request, current_response)
  if (#request >= #REQ_PROGRAM_CLEAR and
	  request:sub(1, #REQ_PROGRAM_CLEAR) == REQ_PROGRAM_CLEAR) then
	sleep(1500) -- trigger the timeout, ProF waits 1000 ms
  end
  return current_response
end
