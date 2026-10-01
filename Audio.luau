-- Audio Module by @Mayko

Audio = Audio or {}
Audio.Url = "http://127.0.0.1:6767"
Audio.Cache = Audio.Cache or {}

local HttpService = game:GetService("HttpService")

if not Audio.Connected then
    Audio.Connected = true
    task.spawn(function()
        while true do
            httppost(Audio.Url .. "/status", "{}", "application/json")
            task.wait(3)
        end
    end)
end

function Audio:Status()
    local res = httppost(self.Url .. "/status", "{}", "application/json")
    if res == "" then
        warn("Server is not running!")
        return false
    end
    local data = HttpService:JSONDecode(res)
    self.Cache = data.cached
    return data
end

function Audio:Get(name, url)
    local payload = type(name) == "table" and { audios = name } or { name = name, url = url }
    local res = httppost(self.Url .. "/get", HttpService:JSONEncode(payload), "application/json")
    if res == "" then
        warn("Server is not running!")
        return false
    end
    local data = HttpService:JSONDecode(res)
    self.Cache = data.cached
    return data
end

function Audio:Play(name, volume, duration)
    task.spawn(function()
        httppost(self.Url .. "/play", HttpService:JSONEncode({
            name = name,
            volume = volume or 1,
            duration = duration or 0
        }), "application/json")
    end)
end

function Audio:Stop(name)
    task.spawn(function()
        httppost(self.Url .. "/stop", name and HttpService:JSONEncode({ name = name }) or "{}", "application/json")
    end)
end

_G.Audio = Audio
return Audio
