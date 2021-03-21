;; GNU Guix development package. This has partly been copied from guile-sparql.
;; To build and install, run:
;;
;;   guix package -f relation-extraction.scm
;;
;; To build it, but not install it, run:
;;
;;   guix build -f relation-extraction.scm
;;
;; To use as the basis for a development environment, run:
;;
;;   guix environment -l relation-extraction.scm
;;

(define-module (relation-extraction)
  #:use-module (guix download)
  #:use-module (guix git-download)
  #:use-module (guix packages)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (guix build-system python)
  #:use-module (guix build-system trivial)
  #:use-module (gnu packages base)
  #:use-module (gnu packages bash)
  #:use-module (gnu packages check)
  #:use-module (gnu packages compression)
  #:use-module (gnu packages databases)
  #:use-module (gnu packages graphviz)
  #:use-module (gnu packages guile)
  #:use-module (gnu packages guile-xyz)
  #:use-module (gnu packages parallel)
  #:use-module (gnu packages python)
  #:use-module (gnu packages python-check)
  #:use-module (gnu packages python-web)
  #:use-module (gnu packages python-xyz)
  #:use-module (gnu packages rdf)
  #:use-module (gnu packages rust-apps)
  #:use-module (ice-9 popen)
  #:use-module (ice-9 rdelim)
  #:use-module (guix gexp)
  #:use-module (guix utils))

(define %source-dir (dirname (current-filename)))

(define-public python-pyfim
  (package
    (name "python-pyfim")
    (version "6.28")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "pyfim" version))
       (sha256
        (base32
         "11ajsx9dswsczxh1xq9k2m5spyf2y8sm8krl5qjc45w3rbcrklbn"))))
    (build-system python-build-system)
    (home-page "http://www.borgelt.net/pyfim.html")
    (synopsis
     "Frequent Item Set Mining and Association Rule Induction for Python")
    (description
     "PyFIM is an extension module that makes several frequent item set mining
implementations available as functions in Python 2.7.x & 3.8.x.  Currently
@url{https://borgelt.net/apriori.html, apriori}, @url{https://borgelt.net/eclat.html, eclat},
@url{https://borgelt.net/fpgrowth.html, fpgrowth}, @url{https://borgelt.net/sam.html, sam},
@url{https://borgelt.net/relim.html, relim}, @url{https://borgelt.net/carpenter.html, carpenter},
@url{https://borgelt.net/ista.html, ista}, @url{https://borgelt.net/accretion.html, accretion} and
@url{https://borgelt.net/apriori.html, apriacc} are available as functions, although the interfaces
do not offer all of the options of the command line program.  (Note that @code{lcm} is available as
an algorithm mode of @code{eclat}).  There is also a \"generic\" function @code{fim}, which is essentially
the same function as @code{fpgrowth}, only with a simplified interface (fewer options).

Finally, there is a function @code{arules} for generating association rules (simplified interface compared
to @code{apriori}, @code{eclat} and @code{fpgrowth}, which can also be used to generate association rules.")
    (license license:expat)))

(define-public python-tweepy
  (package
    (name "python-tweepy")
    (version "3.9.0")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "tweepy" version))
       (sha256
        (base32
         "017nh08n02z13v4vdkqf7yrjx9gqrgcrjpvrkhcpypzk25f9mldz"))))
    (build-system python-build-system)
    (arguments
     `(#:tests? #f))
    (propagated-inputs
     `(("python-requests" ,python-requests)
       ("python-requests-oauthlib"
        ,python-requests-oauthlib)
       ("python-six" ,python-six)))
    (native-inputs
     `(("python-coveralls" ,python-coveralls)
       ("python-mock" ,python-mock)
       ("python-nose" ,python-nose)
       ("python-tox" ,python-tox)
       ("python-vcrpy" ,python-vcrpy)))
    (home-page "https://www.tweepy.org/")
    (synopsis "Twitter library for Python")
    (description "Twitter library for Python")
    (license license:expat)))

(define-public relation-extraction.git
  (let ((version "0.0.0")
        (revision "0")
        (commit (read-line
                 (open-input-pipe "git show HEAD | head -1 | cut -d ' ' -f 2"))))
    (package
      (name "relation-extraction.git")
      (version (git-version version revision commit))
      (source (local-file %source-dir
                          #:recursive? #t
                          #:select? (git-predicate %source-dir)))
      (build-system trivial-build-system)
      (arguments
       `(#:modules ((guix build utils))
         #:builder
         (begin
           (use-modules (guix build utils))
           (let* ((source
                   (lambda (f)
                     (string-append (assoc-ref %build-inputs "source") "/" f)))
                  (output (assoc-ref %outputs "out"))
                  (bindir (string-append output "/bin"))
                  (docdir (string-append output
                                         "/share/doc/relation-extraction-"
                                         ,version))
                  (python-path (lambda (dir)
                                 (string-append dir "/lib/python"
                                                ,(version-major+minor
                                                  (package-version python))
                                                "/site-packages"))))
             (install-file (source "LICENSE") docdir)
             ;; Install documentation
             (for-each
              (lambda (f)
               (install-file f docdir))
              (find-files (source "doc") ".*"))

             ;; Install scripts
             (mkdir-p bindir)
             (copy-recursively (source "bin") bindir)

             ;; We set PATH so later wrap-program will know
             ;; where are the interepreters it's looking for.
             (setenv "PATH" (string-append
                             (assoc-ref %build-inputs "bash")"/bin:"
                             (assoc-ref %build-inputs "python")"/bin:"
                             (getenv "PATH")))

             ;; We wrap all executables with the correct variables,
             ;; containing just the declared inputs.
             (with-directory-excursion bindir
               (for-each
                (lambda (program)
                  (patch-shebang program
                                 (map
                                  (lambda (i)
                                    (string-append (assoc-ref %build-inputs i) "/bin"))
                                  '("bash" "python")))
                  (wrap-program program 
                    `("PATH" ":" =
                      ("$PATH"
                       ,@(map (lambda (input)
                                (let ((store (cdr input)))
                                  (string-append store "/bin" ":"
                                                 store "/sbin")))
                              %build-inputs))))
                  (when (string-suffix? ".py" program)
                    (wrap-program program
                      `("PYTHONPATH" prefix
                        (,@(map (compose python-path cdr)
                            (filter
                             (lambda (input)
                               ;; We only add python inputs to PYTHONPATH.
                               (string-prefix? "python" (car input)))
                             %build-inputs)))))))
                (filter
                 ;; We only wrap user-facing scripts.
                 (lambda (f) (not (string-contains f "/relext/")))
                 (find-files "." ".*\\.(sh|py)")))
               #t)))))
      (propagated-inputs
       `(("bash" ,bash)
         ("coreutils" ,coreutils)
         ("fd" ,fd)
         ("graphviz" ,graphviz)
         ("guile" ,guile-3.0)
         ("guile-sparql" ,guile-sparql)
         ("make" ,gnu-make)
         ("parallel" ,parallel)
         ("pbzip2" ,pbzip2)
         ("python" ,python)
         ("python-numpy" ,python-numpy)
         ("python-pyfim" ,python-pyfim)
         ("python-rdflib" ,python-rdflib)
         ("python-requests" ,python-requests)
         ("python-sqlalchemy" ,python-sqlalchemy)
         ("python-tweepy" ,python-tweepy)
         ("raptor2" ,raptor2)
         ("ripgrep" ,ripgrep)))
      (synopsis
       "Relation extraction workflow")
      (description
       "This package provides the scripts necessary to run the analysis from
@url{https://github.com/fishinthecalculator/relation-extraction}.")
      (home-page
       "https://github.com/fishinthecalculator/relation-extraction")
      (license license:gpl3+))))

relation-extraction.git
