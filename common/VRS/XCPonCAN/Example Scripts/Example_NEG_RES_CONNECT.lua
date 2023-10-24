local counter = 0
local REQ_CONNECT = string.char(0xFF, 0, 0, 0, 0, 0, 0, 0)

function payload_hook(request, current_response)
  if #request >= #REQ_CONNECT then
    if request:sub(1, #REQ_CONNECT) == REQ_CONNECT then
      if 0 == counter then
        counter = counter + 1
        -- no response
        io.write("Payload_Hook::No response\n")
        return false, ""
      elseif 1 == counter then
        counter = counter + 1
        -- error response
        io.write("Payload_Hook::Error response\n")
        return true, string.char(0xFE)
      else
        -- don't change response
        io.write("Payload_Hook::Original response\n")
        return ""
      end
    end
  end
end
