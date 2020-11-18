(use-modules (guix build utils)
             (ice-9 match)
             (ice-9 receive)
             (ice-9 pretty-print)
             (ice-9 rdelim)
             (sparql driver)
             (sparql lang)
             (sparql util)
             (srfi srfi-1)
             (web client)
             (web response)
             (web uri))

(define (interleave a b)
  (if (null? a)
      b
      (cons (car a)
            (interleave b (cdr a)))))

(define %api-key "324b7843-45b3-4d9e-828d-144eaf684d79")

(define (generate-ids prefix number)
  (map
   (lambda (n)
     (string->symbol
      (string-append prefix (number->string n))))
   (iota number)))

(define (describe-query ids)
  (let ((bn (prefix "http://babelnet.org/rdf/"))
        (lemon (prefix "http://www.lemon-model.net/lemon#"))
        (lexinfo (prefix "http://www.lexinfo.net/ontology/2.0/lexinfo#"))
        (rdfs (prefix "http://www.w3.org/2000/01/rdf-schema#")))
    (describe `(,@(map bn ids)))))

(define (select-labels-query ids)
  (let ((bn (prefix "http://babelnet.org/rdf/"))
        (bn-lemon (prefix "http://babelnet.org/model/babelnet#"))
        (rdfs (prefix "http://www.w3.org/2000/01/rdf-schema#"))
        (synsets (generate-ids "s" 5))
        (labels (generate-ids "l" 5))
        (ids (map (lambda (id) (if (string-prefix? "s" id) (string-drop id 1) id)) ids)))
    (select `(,@(interleave synsets labels))
      `(,@(map (lambda (syn id) `(,syn ,(bn-lemon "synsetID") ,(bn id))) synsets ids)
        ,@(map (lambda (syn lab) `(,syn ,(rdfs "label") ,lab)) synsets labels))
        #:distinct #t)))

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

(define* (call-with-line port #:optional (proc #f))
  (let loop ((acc '()))
    (match (read-line port)
      ((? eof-object?) acc)
      (line
       (when proc
         (proc line))
       (loop (cons line acc))))))

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

(define (display-labels ids)
  (call-with-query
   (select-labels-query ids)
   (lambda (port)
     (call-with-line port (lambda (line)
                            (display line)
                            (newline))))))

(define lines
  (call-with-input-file "first_950_babel_ids.txt"
    (lambda (port)
      (map (lambda (l) (string-append "s" l))
           (call-with-line port)))))


(define* (call-with-subsets proc l #:optional (n 5))
 (let loop ((ids l))
  (if (<= (length ids) n)
      (proc ids)
      (receive (n-ids rest)
          (split-at ids n)
        (proc n-ids)
        (loop rest)))))

;; (call-with-subsets (lambda (ids)
;;                      (display-describe ids)
;;                      (sleep 1))
;;                    lines)

;; (call-with-subsets (lambda (ids)
;;                      (display-labels ids)
;;                      (sleep 1))
;;                    lines)

(display (describe-query '("http://example.org#Alice" "http://example.org#Bob")))
