#!/run/current-system/profile/bin/guile \
-e main -s
!#

(define-module (babelnet babelnet-describe-query))

(use-modules (guix build utils)
             (ice-9 getopt-long)
             (ice-9 match)
             (ice-9 receive)
             (ice-9 pretty-print)
             (ice-9 rdelim)
             (ice-9 threads)
             (sparql driver)
             (sparql lang)
             (sparql util)
             (srfi srfi-1)
             (web client)
             (web response)
             (web uri))

(define option-spec
  '((split-token (single-char #\s) (value #t))
    (out-dir (single-char #\o) (value #t))
    (tweets-entities (single-char #\t) (value #t))
    (version (single-char #\v) (value #f))
    (help (single-char #\h) (value #f))))

(define %api-key "324b7843-45b3-4d9e-828d-144eaf684d79")

(define (describe-queryd label)
  (let ((bn (prefix "http://babelnet.org/rdf/"))
        (bn-lemon (prefix "http://babelnet.org/model/babelnet#"))
        (rdfs (prefix "http://www.w3.org/2000/01/rdf-schema#")))
    (describe `(synset)
              `((synset ,(bn-lemon "synsetID") id)
                (synset ,(rdfs "label") ,label)))))

(define* (query-babelnet query
                         #:key
                         (uri "https://babelnet.org/sparql/")
                         (type "text/plain"))
  (http-get
   (string-append uri
                  "?query=" (uri-encode query)
                  "&format=" type
                  "&key=" %api-key)
   #:streaming? #t
   #:headers
   `((user-agent . "GNU Guile")
     (content-type . (application/x-www-form-urlencoded))
     (accept . ((,(string->symbol type)))))))

(define* (call-with-line port #:optional (proc (lambda (x) x)))
  (let loop ((acc '()))
    (match (read-line port)
      ((? eof-object?) acc)
      (line
       (let ((res (proc line)))
         (loop (cons res acc)))))))

(define (call-with-query query proc)
 (receive (header port)
      (query-babelnet query)
    (if (= (response-code header) 200)
        (proc port)
        (begin
          (format #t "Error (~a): ~a~%"
                  (response-code header)
                  (read-line port))
          #f))))

(define (display-describe ids)
  (call-with-query
   (describe-query ids)
   (lambda (port)
     (call-with-line port (lambda (line)
                            (display line)
                            (newline))))))

;; (define lines
;;   (call-with-input-file "first_950_babel_ids.txt"
;;     (lambda (port)
;;       (map (lambda (l) (string-append "s" l))
;;            (call-with-line port)))))


(define* (call-with-subsets proc l #:optional (n 5))
  "Calls PROC over N (or less) elements at a time from L"
 (let loop ((ids l))
  (if (<= (length ids) n)
      (proc ids)
      (receive (n-ids rest)
          (split-at ids n)
        (proc n-ids)
        (loop rest)))))

(define (main args)
  (let* ((options (getopt-long args option-spec))
         (split-token (option-ref options 'split-token #f))
         (out-dir (option-ref options 'out-dir #f))
         (tweets-entities (option-ref options 'tweets-entities #f))
         (tweets
          (call-with-input-file tweets-entities
            (lambda (port)
              (call-with-line port
                              (lambda (line)
                                (let ((row (string-split line #\tab)))
                                  (cons (first row) (last row)))))))))

    (par-map tweets
             (lambda (tweet-pair)
               (let ((tid (car tweet-pair))
                     (tokens (cdr tweet-pair)))
                 (newline))))))
