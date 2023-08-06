(require 'bbdb)

(defun bbdb-export-gmail-filters ()
  (interactive)
  (apply
   'call-process
   "bbdb2gfilter" nil
   (call-interactively 'find-file)
   nil
   (shell-quote-argument user-full-name)
   (shell-quote-argument user-mail-address)
   (append
    (mapcar
     (lambda (record) (bbdb-gmail-filter record "to" 'gnus-public))
     (let ((notes '(gnus-public . ".+")))
       (bbdb-search (bbdb-records) nil nil nil notes)))
    (mapcar
     (lambda (record) (bbdb-gmail-filter record "from" 'gnus-private))
     (let ((notes '(gnus-private . ".+")))
       (bbdb-search (bbdb-records) nil nil nil notes))))))

(defun bbdb-gmail-filter (record name field)
 (combine-and-quote-strings
  (append (list (bbdb-record-getprop record 'timestamp)
                name
                (bbdb-record-getprop record field))
          (bbdb-record-net record))
  ","))

(provide 'rpatterson-gmail)