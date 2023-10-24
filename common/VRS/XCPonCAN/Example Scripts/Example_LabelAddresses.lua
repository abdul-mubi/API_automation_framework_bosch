-- get current script and split into path,file,extension
path,file,extension = string.match(debug.getinfo(1).source, "(.-)([^\\]-([^\\%.]+))$")
-- remove leading '@'
path=string.sub(path,2)
-- add find pattern to package path
package.path = package.path ..";"..path.."?.lua"
-- load module
LabelAddresses = require "LabelAddresses"
-- use label
print("M_U8_3_Shared_Cal_Measure is at " .. 
         LabelAddresses.M_U8_3_Shared_Cal_Measure)
