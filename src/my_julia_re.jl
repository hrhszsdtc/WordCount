module MyJuliaRe

export re_sub
export re_findall

function re_sub(pattern, repl, string, count=0)
    if isa(repl, Function)
        repl = m -> repl(m.match)
    end
    if count == 0
        return replace(string, Regex(pattern) => repl)
    else
        n=0
        return replace(string, Regex(pattern) => m -> begin
            n += 1
            if n <= count
                repl(m)
            else
                return m.match
            end
        end)
    end
end

function re_findall(pattern, string)
    return [m.match for m in eachmatch(Regex(pattern), string)]
end

end