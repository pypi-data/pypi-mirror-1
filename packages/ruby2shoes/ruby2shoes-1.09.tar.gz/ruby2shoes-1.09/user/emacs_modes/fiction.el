;; fiction.el --- novel- and story-writing mode for Emacs
;; Copyright (C) 2003 - Ruby Dos Zapatas - Version 1.0

;; This file is released under the GNU General Public License and is
;; free software; you can redistribute it and/or modify it under the
;; terms of the GNU General Public License as published by the Free
;; Software Foundation; either version 2, or (at your option) any later
;; version.

;; It is distributed in the hope that it will be useful, but WITHOUT ANY
;; WARRANTY; without even the implied warranty of MERCHANTABILITY or
;; FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
;; for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs; see the file COPYING.  If not, write to the
;; Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
;; MA 02111-1307, USA.

;; Usage: Put the following lines in your ~/.emacs file:
;; ---
;;      (load "/your/path/to/emacs-dir/fiction")
;;      (setq auto-mode-alist
;;            (cons '("\\.fc" . fiction-mode) auto-mode-alist)) 
;; ---
;; The load command causes emacs to load this file. The setq
;; identifies files having extension ".fc" with this mode.

;;
;; menu-bar access to keymap for the rodent-oriented user
;;
(defvar fiction-mode-menu-bar-map nil)
(if fiction-mode-menu-bar-map
	nil
  (setq fiction-mode-menu-bar-map (make-sparse-keymap))
  
  (define-key fiction-mode-menu-bar-map [bits]
	(cons "Bits" (make-sparse-keymap "Bits")))
  
  (define-key fiction-mode-menu-bar-map [bits fiction-novel-skeleton]
	'("New Novel MS." . fiction-novel-skeleton))
  (define-key fiction-mode-menu-bar-map [bits fiction-story-skeleton]
	'("New Story MS." . fiction-story-skeleton))
  (define-key fiction-mode-menu-bar-map [bits fiction-style-acknowledgements]
	'("Acknowledgements Page" . fiction-style-acknowledgements))
  (define-key fiction-mode-menu-bar-map [bits fiction-style-dedication]
	'("Dedication Page" . fiction-style-dedication))
  (define-key fiction-mode-menu-bar-map [bits fiction-style-epigraph]
	'("Epigraph Page" . fiction-style-epigraph))
  (define-key fiction-mode-menu-bar-map [bits fiction-notes]
	'("Non-printing Notes Line" . fiction-notes))
  (define-key fiction-mode-menu-bar-map [bits fiction-outline]
	'("Outline Line" . fiction-outline))
  (define-key fiction-mode-menu-bar-map [bits fiction-asterisks]
	'("Asterisks" . fiction-asterisks))
  (define-key fiction-mode-menu-bar-map [bits fiction-newpage]
	'("Force New Page" . fiction-newpage))
  (define-key fiction-mode-menu-bar-map [bits fiction-newline]
	'("Force New Line" . fiction-newline))
  (define-key fiction-mode-menu-bar-map [bits fiction-count-words]
	'("Wordcount" . fiction-count-words))
  (define-key fiction-mode-menu-bar-map [bits fiction-insert-marker]
	'("Edit Marker" . fiction-insert-marker))
  (define-key fiction-mode-menu-bar-map [bits fiction-goto-marker]
	'("Go to Edit Marker" . fiction-goto-marker))
  (define-key fiction-mode-menu-bar-map [bits fiction-insert-marker2]
	'("Edit Marker 2" . fiction-insert-marker2))
  (define-key fiction-mode-menu-bar-map [bits fiction-goto-marker2]
	'("Go to Edit Marker 2" . fiction-goto-marker2))
  
  (define-key fiction-mode-menu-bar-map [style]
	(cons "Style" (make-sparse-keymap "Style")))
  
  (define-key fiction-mode-menu-bar-map [style fiction-style-part]
	'("Part" . fiction-style-part))
  (define-key fiction-mode-menu-bar-map [style fiction-style-chapter]
	'("Chapter" . fiction-style-chapter))
  (define-key fiction-mode-menu-bar-map [style fiction-style-section]
	'("Section" . fiction-style-section))
  (define-key fiction-mode-menu-bar-map [style fiction-style-subsection]
	'("Subsection" . fiction-style-subsection))
  (define-key fiction-mode-menu-bar-map [style fiction-style-quotation]
	'("Quotation" . fiction-style-quotation))
  (define-key fiction-mode-menu-bar-map [style fiction-style-quote]
	'("Quote" . fiction-style-quote))
  (define-key fiction-mode-menu-bar-map [style fiction-style-verse]
	'("Verse" . fiction-style-verse))
  (define-key fiction-mode-menu-bar-map [style fiction-style-paragraph]
	'("New Paragraph" . fiction-style-paragraph))
  )

;;
;; key map preserves C-s,d,t,a,f,b from outline-mode

(defvar fiction-mode-prefix-map nil)
(if fiction-mode-prefix-map
	nil
  (setq fiction-mode-prefix-map (make-sparse-keymap))
  (define-key fiction-mode-prefix-map "\C-b" 'fiction-style-subsection) 
  (define-key fiction-mode-prefix-map "\C-c" 'fiction-style-chapter)   
  (define-key fiction-mode-prefix-map "\C-e" 'fiction-style-epigraph)
  (define-key fiction-mode-prefix-map "\C-i" 'fiction-style-dedication)
  (define-key fiction-mode-prefix-map "\C-k" 'fiction-goto-marker2)
  (define-key fiction-mode-prefix-map "\C-l" 'fiction-style-acknowledgements)
  (define-key fiction-mode-prefix-map "\C-m" 'fiction-insert-marker2)
  (define-key fiction-mode-prefix-map "\C-n" 'fiction-style-section) 
  (define-key fiction-mode-prefix-map "\C-o" 'fiction-style-quote)    
  (define-key fiction-mode-prefix-map "\C-p" 'fiction-style-part)      
  (define-key fiction-mode-prefix-map "\C-u" 'fiction-emphasis) 
  (define-key fiction-mode-prefix-map "\C-v" 'fiction-style-verse)
  (define-key fiction-mode-prefix-map "\C-w" 'fiction-style-quotation)
  )

(defvar fiction-mode-map nil )
(if fiction-mode-map
	nil
  (setq fiction-mode-map (make-sparse-keymap))
  (define-key fiction-mode-map [menu-bar] fiction-mode-menu-bar-map)
  (define-key fiction-mode-map "\C-c" fiction-mode-prefix-map)
  (define-key fiction-mode-map "\C-[\C-m" 'fiction-style-paragraph)  
  (define-key fiction-mode-map "\M-1" 'fiction-novel-skeleton)
  (define-key fiction-mode-map "\M-2" 'fiction-story-skeleton)
  (define-key fiction-mode-map "\M-8" 'fiction-asterisks)
  (define-key fiction-mode-map "\M-9" 'fiction-newpage)
  (define-key fiction-mode-map "\M-0" 'fiction-newline)
  (define-key fiction-mode-map "\M-k" 'fiction-goto-marker)
  (define-key fiction-mode-map "\M-m" 'fiction-insert-marker)
  (define-key fiction-mode-map "\M-n" 'fiction-notes)
  (define-key fiction-mode-map "\M-o" 'fiction-outline)
  (define-key fiction-mode-map "\M-p" 'fiction-count-words)
  )

(define-derived-mode fiction-mode outline-mode "Fiction"
"Major mode for writing novels, children's stories, and other fiction.
Creates .fc files which are translated into LaTeX, dvi, ps, HTML and
text by external Python scripts.

Begin with M-1, the fiction skeleton.  Skeletons repeat a prompt until
they get an empty string - it's an Emacs thing.  Skeleton expects ONE
LINE title and chapter name.  But part, chapter and other titles can be
two lines long, just add another line below the asterisked one for
subtitles and such. Line-breaks are maintained in these two-line
titles. Use the skeleton author-prompt for multiple authors.

Mode is derived from outline.el which is derived from text.el. So many
benefits of those modes remain in the keymap. Chapters, sections, and
subsections are first-level outline elements and show their titles.  So
you can use single-* lines to outline your work. The second character of
these lines MUST be a space, i.e.: `* outline stuff'. Mode also ignores
lines beginning with pound-sign so that you can make notes within the
manuscript. M-n creates a new note-line.

Mode needs to identify normal paragraphs; use M-Return to begin them.
The only emphasis is underlining. To underline a word, begin it with an
underbar: this underlined is _this.  Use M-0 for forcing a line-break
outside of verse, quotes, and quotations and M-9 for forcing a new page.
M-8 inserts an asterisk-spacer, three asterisks in a centered paragraph.

If the mode becomes sluggish, as it will with larger novels on slower
machines, turn off the global font lock in Emac's Edit menu.  The
sluggishness comes from the way Emacs colors your fonts and turning off
the color returns you to normal, lightning-like speed.

Commands:\\{fiction-mode-map}
"
  (set-fill-column 80)
  (auto-fill-mode)
)
;;
;; style functions-----------------------------
;;
(defun fiction-style-part (title)
  "Part: page with only a title on it."
  (interactive "sPart title: ")
  (insert "\n*part+: " title )
  )

(defun fiction-style-chapter (title)
  "Chapter: new page with title and text."
  (interactive "sChapter title: ")
  (insert "\n*chapter+: " title )
  )

(defun fiction-style-section (title)
  "Section: title following previous paragraph."
  (interactive "sSection title: ")
  (insert "\n*section+:   " title)
  )

(defun fiction-style-subsection (title)
  "Subsection: smaller title following previous paragraph."
  (interactive "sSubsection title: ")
  (insert "\n**subsection+:     " title)
  )

(defun fiction-style-paragraph ()
  "Normal paragraph."
  (interactive)
  (insert "\n***paragraph\n")
  (recenter)
  )

(defun fiction-style-quotation ()
  "Mark bounded lines as quotation: First line indented."
  (interactive)
  (insert "\n****begin_quotation")
  (insert "\n****end_quotation")
  (beginning-of-line)
  )

(defun fiction-style-quote ()
  "Mark bounded lines as quote."
  (interactive)
  (insert "\n****begin_quote")
  (insert "\n****end_quote")
  (beginning-of-line)
  )

(defun fiction-style-verse ()
  "Mark bounded lines as verse"
  (interactive)
  (insert "\n****begin_verse")
  (insert "\n****end_verse")
  (beginning-of-line)
  )

(defun fiction-style-acknowledgements ()
  "Acknowledgement page."
  (interactive)
  (fiction-newpage)
  (fiction-style-subsection "Acknowledgements")
  )

(defun fiction-style-dedication ()
  "Dedication page."
  (interactive)
  (fiction-newpage)
  (fiction-style-subsection "Dedication")
  )

(defun fiction-style-epigraph ()
  "Epigraph page."
  (interactive)
  (fiction-newpage)
  (fiction-style-subsection "Epigraph")
  (fiction-style-quotation)
  )

;;
;; bits ------------------------
;;
(defun fiction-notes()
  "New line with pound-sign for outline notes"
  (interactive)
  (end-of-line)
  (insert "\n# ")
  )

(defun fiction-outline()
  "New line with asterisk for outline"
  (interactive)
  (end-of-line)
  (insert "\n* ")
  )

(defun fiction-newpage ()
  (interactive)
  (insert "\n****\\newpage")
  )

(defun fiction-asterisks ()
  (interactive)
  (insert "\n****\\asterisks")
  (fiction-style-paragraph)
  )

(defun fiction-newline ()
  (interactive)
  (insert "\n****\\newline")
  )

(defun fiction-emphasis ()
  (interactive)
  (insert "_")
  (forward-word 2)
  (backward-word 1)
  )

;;
;; skeletons for necessary outer LaTeX elements
;;
(define-skeleton fiction-novel-skeleton "Novel Boiler Plate"
  "Title: "
  "*novel\n*title: " str "\n**author(s): "
  ("Author(s): "
  str )
  "\n**copyright: "
  ("Copyright: "
  str )
  ("Chapter name: "
  "\n*chapter+: " str _)
)

(define-skeleton fiction-story-skeleton "Story Boiler Plate"
  "Title: "
  "*story\n*title: " str "\n**author(s): "
  ("Authors: "
  str)
  "\n**copyright: "
  ("Copyright: "
  str "\n" _)
)

;;
;; utility methods
;;

(defvar fiction-edit-marker "# [ -- EDIT MARKER -- ]")

(defun fiction-insert-marker ()
  "Insert or move edit marker"
  (interactive)
  ;; remove last marker
  (push-mark)
  (beginning-of-buffer)
  (if (search-forward fiction-edit-marker nil t)
	  (progn
		(beginning-of-line)
		(kill-line 1)
		)
	)
  ;; insert new marker
  (exchange-point-and-mark-nomark)
  (beginning-of-line)
  (insert fiction-edit-marker)
  (insert "\n")
  )

(defun fiction-goto-marker ()
  "Find edit marker"
  (interactive)
  (beginning-of-buffer)
  (search-forward fiction-edit-marker)
  (beginning-of-line)
  )
  
(defvar fiction-edit-marker2 "# [ -- EDIT MARKER 2 -- ]")

(defun fiction-insert-marker2 ()
  "Insert or move second edit marker"
  (interactive)
  ;; remove last marker
  (push-mark)
  (beginning-of-buffer)
  (if (search-forward fiction-edit-marker2 nil t)
	  (progn
		(beginning-of-line)
		(kill-line 1)
		)
	)
  ;; insert new marker
  (exchange-point-and-mark-nomark)
  (beginning-of-line)
  (insert fiction-edit-marker2)
  (insert "\n")
  )

(defun fiction-goto-marker2 ()
  "Find final edit marker"
  (interactive)
  (beginning-of-buffer)
  (search-forward fiction-edit-marker2)
  (beginning-of-line)
  )
  
(defun fiction-count-words ()
  "Print number of words in MS."
  (interactive)
  (message "Counting words in MS ... ")
  (save-excursion
	(let ((count 0))
	  (goto-line 1)
	  (while (= (forward-line 1) 0)
		(if (or (eq  (char-after)  42)  ; *
				(eq  (char-after)  35)  ; #
				(eq  (char-after)  47)  ; /
				(eq  (char-after)  10)) ; \n
			nil
			(while (and (< (point) (line-end-position))
						(re-search-forward "\\w+\\W*" (line-end-position) t))
			  (setq count (1+ count)))
			))
	  (cond ((zerop count)
			 (message
			  "Word count: 0"))
			((= 1 count)
			 (message
			  "Word count: 1"))
			(t
			 (message
			  "Word count: %d" count))))))

;; end of fiction.el
