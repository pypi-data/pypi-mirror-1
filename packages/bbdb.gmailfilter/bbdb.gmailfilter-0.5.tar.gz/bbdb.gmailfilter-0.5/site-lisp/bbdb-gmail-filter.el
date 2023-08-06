(require 'bbdb)

(defun bbdb-export-gmail-filters ()
  (interactive)
  (apply
   'call-process
   "bbdb2gfilter" nil
   (call-interactively 'find-file)
   nil
   user-full-name
   user-mail-address
   (append
    (bbdb-gmail-filters "to" 'gnus-public)
    (bbdb-gmail-filters "from" 'gnus-private))))

(defun bbdb-gmail-filters (name field)
  (mapcar
   (lambda (record) (bbdb-gmail-filter record name field))
   (bbdb-search-gmail-labels field)))

(defun bbdb-gmail-filter (record name field)
  (concat
   (combine-and-quote-strings
    (list (bbdb-record-getprop record 'timestamp)
          name
          (bbdb-record-getprop record field))
    ",")
   ","
   (mapconcat
    (lambda (net) (bbdb-dwim-net-address record net))
    (or (bbdb-record-net record) (list ""))
    ",")))

(defun bbdb-search-gmail-labels (field)
  (let ((notes (cons field ".+")))
    (remove-if
     (lambda (record) (bbdb-record-gmail-labelp record field))
     (bbdb-search (bbdb-records) nil nil nil notes))))

(defun bbdb-record-gmail-labelp (record bbdb-field)
  (let* ((field (bbdb-record-getprop record bbdb-field))
         (sexp (when field
                 (condition-case nil (read field) (error nil)))))
    (consp sexp)))

(provide 'bbdb-gmail-filter)