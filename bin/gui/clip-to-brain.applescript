-- Clip to Brain — AppleScript front end for bin/brain-clip.sh.
--
-- Two ways to use the built "Clip to Brain.app":
--   • Double-click (or Spotlight / Dock / Finder-toolbar) → clips whatever is on the
--     clipboard (a URL or text); if the clipboard is empty it asks you to paste/type.
--   • Drag files or PDFs onto the icon → each is copied into sources/ (+ .meta.md).
--
-- @@SCRIPT@@ and @@PATH@@ are substituted with absolute values by brain-clip-gui.sh at
-- build time, so the app keeps working no matter where it is launched from.

property scriptPath : "@@SCRIPT@@"
property shellPrefix : "export PATH=@@PATH@@; "

-- Run brain-clip.sh with one argument; return its stdout (or "ERROR: ...").
on clipOne(arg)
	try
		return do shell script shellPrefix & quoted form of scriptPath & " " & quoted form of arg
	on error errMsg
		return "ERROR: " & errMsg
	end try
end clipOne

-- Last non-empty line of brain-clip's output = the "wrote sources/..." confirmation.
on lastLine(t)
	set paras to paragraphs of t
	repeat with i from (count paras) to 1 by -1
		if (item i of paras) is not "" then return item i of paras
	end repeat
	return t
end lastLine

on notify(msg)
	display notification msg with title "Clip to Brain"
end notify

-- Double-click / launch: clip the clipboard, prompting if it is empty.
on run
	set clip to ""
	try
		set clip to (the clipboard as text)
	end try
	if clip is "" then
		try
			set clip to text returned of (display dialog ¬
				"Paste a URL or type a note to clip into the brain:" default answer "" ¬
				with title "Clip to Brain" buttons {"Cancel", "Clip"} default button "Clip")
		on error
			return -- user cancelled
		end try
	end if
	if clip is "" then return
	notify(lastLine(clipOne(clip)))
end run

-- Drag-and-drop: clip each dropped file / folder item.
on open theItems
	set okCount to 0
	repeat with f in theItems
		set res to clipOne(POSIX path of f)
		if res does not start with "ERROR" then set okCount to okCount + 1
	end repeat
	notify(("clipped " & (okCount as text) & " of " & (count theItems) as text) & " item(s) to sources/")
end open
