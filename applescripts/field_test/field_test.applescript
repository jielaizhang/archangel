-- field_test.applescript
-- field_test

--  Created by James Schombert on 1/12/09.
--  Copyright 2009 Univ. of Oregon. All rights reserved.

on awake from nib theObject
	set fileName to (path to documents folder as string) & "tmp.tmp"
	set fileID to open for access file fileName
	set dataFromFile to read fileID as string
	close access fileID
	set position of window 1 to {25, 200}
	tell text view "TextOutput" of scroll view "TextOutput" of window 1
		set text color to {0, 65535, 0}
		set theFont to call method "fontWithName:size:" of class "NSFont" with parameters {"Courier", 12}
		call method "setFont:" of object it with parameter theFont
	end tell
	set the contents of text view "TextOutput" of scroll view "TextOutput" of window 1 to dataFromFile
end awake from nib