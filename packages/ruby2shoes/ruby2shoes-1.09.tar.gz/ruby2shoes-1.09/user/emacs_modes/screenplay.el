;; screenplay.el --- Hollywood spec-script mode for Emacs
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
;;      (load "/your/path/to/emacs-dir/screenplay")
;;      (setq auto-mode-alist
;;            (cons '("\\.sp" . screenplay-mode) auto-mode-alist)) 
;; ---
;; The load command causes emacs to load this file. The setq
;; identifies files having extension ".sp" with this mode.

;;
;; menu-bar access to keymap for the rodent-oriented user
;;
(defvar screenplay-mode-menu-bar-map nil)
(if screenplay-mode-menu-bar-map
	nil
  (setq screenplay-mode-menu-bar-map (make-sparse-keymap))
  
  (define-key screenplay-mode-menu-bar-map [play]
	(cons "Play" (make-sparse-keymap "Play")))
  
  (define-key screenplay-mode-menu-bar-map [play screenplay-skeleton-tv60]
	'("Teleplay (60 min.)" . screenplay-skeleton-tv60))
  (define-key screenplay-mode-menu-bar-map [play screenplay-skeleton-tv30]
	'("Teleplay (30 min.)" . screenplay-skeleton-tv30))
  (define-key screenplay-mode-menu-bar-map [play screenplay-skeleton-movie]
	'("Screenplay" . screenplay-skeleton-movie))
  
  (define-key screenplay-mode-menu-bar-map [bits]
	(cons "Bits" (make-sparse-keymap "Bits")))
  
  (define-key screenplay-mode-menu-bar-map [bits screenplay-day]
	'("- DAY" . screenplay-day))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-night]
	'("- NIGHT" . screenplay-night))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-continuous]
	'("- CONTINUOUS" . screenplay-continuous))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-voiceover]
	'("(V.O.)" . screenplay-voiceover))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-offscreen]
	'("(O.S.)" . screenplay-offscreen))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-insert-marker]
	'("Edit Marker" . screenplay-insert-marker))
  (define-key screenplay-mode-menu-bar-map [bits screenplay-goto-marker]
	'("Go to Edit Marker" . screenplay-goto-marker))

  (define-key screenplay-mode-menu-bar-map [style]
	(cons "Style" (make-sparse-keymap "Style")))
  
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-exteriorshot]
	'("EXT." . screenplay-style-exteriorshot))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-interiorshot]
	'("INT." . screenplay-style-interiorshot))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-narrative]
	'("Action Slug" . screenplay-style-narrative))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-parenthetical]
	'("Parenthetical" . screenplay-style-parenthetical))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-titleover]
	'("Title Over:" . screenplay-style-titleover))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-flushright]
	'("Transition" . screenplay-style-flushright))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-continuing]
	'("CONT'D" . screenplay-style-continuing))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-speaker]
	'("Character Slug" . screenplay-style-speaker))
  (define-key screenplay-mode-menu-bar-map [style screenplay-style-alternate]
	'("Alternate Speakers" . screenplay-style-alternate))
  )

;;
;; key map preserves C-s,d,t,a,f,b from outline-mode
;; and so uses: a,b,c,d,e,f,g,i,n,p,o,r,s,t

(defvar screenplay-mode-prefix-map nil)
(if screenplay-mode-prefix-map
	nil
  (setq screenplay-mode-prefix-map (make-sparse-keymap))
  (define-key screenplay-mode-prefix-map "\C-c" 'screenplay-style-speaker)      
  (define-key screenplay-mode-prefix-map "\C-u" 'screenplay-style-continuing)   
  (define-key screenplay-mode-prefix-map "\C-e" 'screenplay-style-exteriorshot) 
  (define-key screenplay-mode-prefix-map "\C-i" 'screenplay-style-interiorshot) 
  (define-key screenplay-mode-prefix-map "\C-k" 'screenplay-contd) 
  (define-key screenplay-mode-prefix-map "\C-m" 'screenplay-emphasis) 
  (define-key screenplay-mode-prefix-map "\C-n" 'screenplay-style-narrative)    
  (define-key screenplay-mode-prefix-map "\C-p" 'screenplay-style-parenthetical)
  (define-key screenplay-mode-prefix-map "\C-o" 'screenplay-style-titleover)   
  (define-key screenplay-mode-prefix-map "\C-r" 'screenplay-style-flushright)   
  (define-key screenplay-mode-prefix-map "\C-v" 'screenplay-voiceover)   
  (define-key screenplay-mode-prefix-map "\C-x" 'screenplay-offscreen)   
  )

(defvar screenplay-mode-map nil )
(if screenplay-mode-map
	nil
  (setq screenplay-mode-map (make-sparse-keymap))
  (define-key screenplay-mode-map [menu-bar] screenplay-mode-menu-bar-map)
  (define-key screenplay-mode-map "\C-c" screenplay-mode-prefix-map)
  (define-key screenplay-mode-map "\M-q" 'screenplay-fill-narrative)
  (define-key screenplay-mode-map "\C-q" 'screenplay-fill-dialogue)
  (define-key screenplay-mode-map "\C-[\C-m" 'screenplay-style-alternate)  
  (define-key screenplay-mode-map "\M-1" 'screenplay-skeleton-movie)
  (define-key screenplay-mode-map "\M-2" 'screenplay-skeleton-tv30)
  (define-key screenplay-mode-map "\M-3" 'screenplay-skeleton-tv60)
  (define-key screenplay-mode-map "\M-8" 'screenplay-day)
  (define-key screenplay-mode-map "\M-9" 'screenplay-night)
  (define-key screenplay-mode-map "\M-0" 'screenplay-continuous)
  (define-key screenplay-mode-map "\M-n" 'screenplay-notes)
  (define-key screenplay-mode-map "\M-p" 'screenplay-count-pages)
  (define-key screenplay-mode-map "\M-g" 'screenplay-goto-marker)
  (define-key screenplay-mode-map "\M-m" 'screenplay-insert-marker)
  )

(define-derived-mode screenplay-mode outline-mode "Screenplay"
"Major mode for writing industry-standard Hollywood spec-scripts.
Creates .sp files which are translated into LaTeX, dvi, PostScript, HTML
and text by external Python scripts. The resulting screenplays are
identical in format and appearance to the products of ScriptThing,
FinalDraft, and other professional scriptwriting software.

The .sp files can be either *movie* (95 pages plus) or *tv* (30 or 60
minute) scripts.  The Play menu skeletons determine this, marking the
first line of the file with the type for the benefit of the conversion
scripts. Skeletons repeat a prompt until they get an empty string - it's
an Emacs thing.  Mode expects ONE-LINE title, series, and episode.  But
use the skeleton author prompt for multiple authors and the contact-info
prompt for address, phone and email lines in the address paragraph of
the title page.

Mode is WYSISWYG [S for sort-of] and uses auto-fill-mode to maintain
margins. It is derived from outline.el which is derived from text.el. So
many benefits of those modes remain in the keymap. Scenes --scene, int.,
ext.-- are second-level outline elements. Mode ignores lines beginning
in asterisks that have more than one token. So you can use single-*
lines to outline your screenplay. Mode also ignores lines beginning with
# so that you can make notes within the script. M-n creates a new
note-line.

Mode tracks the last two speakers and M-Return alternates them. It also
tracks the last exterior and last interior location.  Enter a period at
the INT. or EXT. location-prompt to get the last location automatically
--then hit M-0 for the dash-CONTINUOUS.  Cool, no?

The only emphasis in a spec-script is underlining. To underline a word,
begin it with an underbar: this underlined is _this.  LaTeX commands
like \newpage take the form *\command on a line by themselves.  The
backslash in the second position is the key.

Commands:\\{screenplay-mode-map}
"
  (setq tab-width 5)
  (auto-fill-mode)
)
;;
;; style functions-----------------------------
;;
(defvar screenplay-last-exterior nil)
(defvar screenplay-last-interior nil)

(defun screenplay-style-interiorshot (location)
  "Mark following paragraph as interiorshot"
  (interactive "sLocation: ")
  (if (string= location ".")
	(setq location screenplay-last-interior)
	(progn (setq location (upcase location))
		   (setq screenplay-last-interior location))
	)
  (insert "\n**interiorshot\nINT. " location)
  (insert "\n***description\n")
  (set-fill-column 70)
  (previous-line 2)
  (end-of-line)
  )

(defun screenplay-style-exteriorshot (location)
  "Mark following paragraph as exteriorshot"
  (interactive "sLocation: ")
  (if (string= location ".")
	(setq location screenplay-last-exterior)
	(progn (setq location (upcase location))
		   (setq screenplay-last-exterior location))
	)
  (insert "\n**exteriorshot\nEXT. " location)
  (insert "\n***description\n")
  (set-fill-column 70)
  (previous-line 2)
  (end-of-line)
  )

(defvar screenplay-last-speaker nil)
(defvar screenplay-next2last-speaker nil)
(defvar screenplay-tempvar nil)

(defun screenplay-style-speaker (name)
  "Mark following paragraph as speaker"
  (interactive "sSpeaker: ")
  (setq name (upcase name))
  (setq screenplay-next2last-speaker screenplay-last-speaker)
  (setq screenplay-last-speaker name)
  (insert "\n***speaker\n\t\t\t\t\t" name)
  (set-fill-column 50)
  (insert "\n***dialogue\n\t\t")
  )

(defun screenplay-style-alternate ()
  "Mark following paragraph as speaker"
  (interactive)
  (insert "\n***speaker\n\t\t\t\t\t" screenplay-next2last-speaker)
  (set-fill-column 50)
  (setq screenplay-tempvar screenplay-next2last-speaker)
  (setq screenplay-next2last-speaker screenplay-last-speaker)
  (setq screenplay-last-speaker screenplay-tempvar)
  (insert "\n***dialogue\n\t\t")
  )

(defun screenplay-style-continuing ()
  "Mark following paragraph as continuing"
  (interactive)
  (insert "\n***continuing\n\t\t\t\t\t" screenplay-last-speaker " (CONT'D)")
  (set-fill-column 50)
  (insert "\n***dialogue\n\t\t")
  )

(defun screenplay-style-narrative ()
  "Mark following paragraph as narrative"
  (interactive)
  (set-fill-column 70)
  (insert "\n***narrative\n")
  )

(defun screenplay-style-parenthetical ()
  "Mark following paragraph as parenthetical"
  (interactive)
  (set-fill-column 40)
  (previous-line 2)
  (end-of-line)
  (insert "\n***parenthetical\n\t\t\t\t()")
  (backward-char)
  )

(defun screenplay-style-titleover ()
  "Mark following paragraph as titleover"
  (interactive)
  (set-fill-column 60)
  (insert "\n***titleover\n")
  (insert "Title Over:\n\t\t\t")
  )

(defun screenplay-style-flushright (transition)
  "Mark following paragraph as flushright"
  (interactive "sTransition: ")
  (setq transition (upcase transition))
  (set-fill-column 80)
  (insert "\n***flushright\n\t\t\t\t\t\t\t\t\t\t" transition)
  )

;;
;; bits ------------------------
;;
(defun screenplay-day ()
  (interactive)
  (insert " - DAY")
  (next-line 2)
  )

(defun screenplay-night ()
  (interactive)
  (insert " - NIGHT")
  (next-line 2)
  )

(defun screenplay-continuous ()
  (interactive)
  (insert " - CONTINUOUS")
  (next-line 2)
  )

(defun screenplay-contd ()
  (interactive)
  (backward-kill-word 1)
  (insert "continuing")
  (next-line 1)
  (end-of-line)
  (insert " (CONT'D)")
  (next-line 2)
  )

(defun screenplay-voiceover ()
  (interactive)
  (previous-line 2)
  (end-of-line)
  (insert " (V.O.)")
  (next-line 2)
  (setq screenplay-last-speaker (concat screenplay-last-speaker " (V.O.)"))
  )

(defun screenplay-offscreen ()
  (interactive)
  (previous-line 2)
  (end-of-line)
  (insert " (O.S.)")
  (next-line 2)
  (setq screenplay-last-speaker (concat screenplay-last-speaker " (O.S.)"))
  )

(defun screenplay-emphasis ()
  (interactive)
  (insert "_")
  (forward-word 2)
  (backward-word 1)
  )

(defun screenplay-fill-dialogue ()
  (interactive)
  (set-fill-column 50)
  (fill-paragraph t)
  )

(defun screenplay-fill-narrative ()
  (interactive)
  (set-fill-column 70)
  (fill-paragraph t)
  )

;;
;; skeletons for necessary outer LaTeX elements
;;
(define-skeleton screenplay-skeleton-movie "Screenplay Boiler Plate"
  "Title: "
  "*movie\n*title: " str "\n**author(s): "
  ("Author(s): "
  str )
  "\n**copyright: "
  ("Copyright: "
  str )
  "\n**address"
  ("Contact info: "
  "\n" str)
  "\n*fadein\nFADE IN:"_"\n*fadeout\nFADE OUT"
)

(define-skeleton screenplay-skeleton-tv30 "30-Minute Teleplay Boiler Plate"
  "Title: "
  "*tv\n*title: " str "\n**author(s): "
  ("Author(s): "
  str )
  "\n**copyright: "
  ("Copyright: "
  str )
  "\n**address"
  ("Contact info: "
  "\n" str)
  "\n**scene\nTeaser (3 pages)"_
  "\n_End _of _Teaser"
  "\n*\\newpage"
  "\n**scene\nAct One (9 pages)"
  "\n_End _of _Act _One"
  "\n*\\newpage"
  "\n**scene\nAct Two (9 pages)"
  "\n_End _of _Act _Two"
  "\n*\\newpage"
  "\n**scene\nTag (1 page)"
  "\n_End _of _Tag"
)

(define-skeleton screenplay-skeleton-tv60 "60-Minute Teleplay Boiler Plate"
  "Title: "
  "*tv\n*title: " str "\n**author(s): "
  ("Author(s): "
  str )
  "\n**copyright: "
  ("Copyright: "
  str )
  "\n**address"
  ("Contact info: "
  "\n" str)
  "\n**scene\nTeaser (2 pages)"_
  "\n_End _of _Teaser"
  "\n*\\newpage"
  "\n**scene\nAct One (10 pages)"
  "\n_End _of _Act _One"
  "\n*\\newpage"
  "\n**scene\nAct Two (8 pages)"
  "\n_End _of _Act _Two"
  "\n*\\newpage"
  "\n**scene\nAct Three (12 pages)"
  "\n_End _of _Act _Three"
  "\n*\\newpage"
  "\n**scene\nAct Four (12 pages)"
  "\n_End _of _Act _Four"
)

;;
;; utility methods
;;
(defun screenplay-count-pages ()
  "Print number of pages for script."
  (interactive)
  (message "Counting pages ... ")
  (save-excursion
	(let ((count 0) (pages 0) (partial 0))
	  (goto-line 1)
	  (while (= (forward-line 1) 0)
		(if (or (eq  (char-after)  42)  ; *
				(eq  (char-after)  35)  ; #
				(eq  (char-after)  10)) ; \n
			nil
			(progn (setq count (1+ count))
				   (if (= count 28)
					 (progn (setq count 0)
							(setq pages (1+ pages)))))))
	  (setq partial (/ (* count 10) 28))
			 (message
			  "Page count: %d.%d" pages partial))))

(defun screenplay-notes()
  "New line with pound-sign for outline notes"
  (interactive)
  (end-of-line)
  (insert "\n# ")
  )

(defvar screenplay-edit-marker "# [ -- EDIT MARKER -- ]")

(defun screenplay-insert-marker ()
  "Insert or move edit marker"
  (interactive)
  ;; remove last marker
  (push-mark)
  (beginning-of-buffer)
  (if (search-forward screenplay-edit-marker nil t)
	  (progn
		(beginning-of-line)
		(kill-line 1)
		)
	)
  ;; insert new marker
  (exchange-point-and-mark-nomark)
  (beginning-of-line)
  (insert screenplay-edit-marker)
  (insert "\n")
  )

(defun screenplay-goto-marker ()
  "Find edit marker"
  (interactive)
  (beginning-of-buffer)
  (search-forward screenplay-edit-marker)
  (beginning-of-line)
  )
  
;; end of screenplay.el  (Th-th-th-that's all folks!)
