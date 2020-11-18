(use-modules (guix download)
             (guix git-download)
             (guix packages)
             ((guix licenses) #:prefix license:)
             (guix build-system python)
             (gnu packages python-check)
	         (gnu packages check)
	         (gnu packages python-web)
	         (gnu packages python-xyz))

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

;; (define-public python-efficient-apriori
;;   ;; Upstream didn't tag latest release.
;;   (let ((revision "0")
;;         (commit "4fcdd38fd487a2183ad42ead9a14ee7641e43914"))
;;     (package
;;    (name "python-efficient-apriori")
;;    (version (git-version "1.1.1" revision commit))
;;    (source
;;       (origin
;;         (method git-fetch)
;;         (uri (git-reference
;;                (url "https://github.com/tommyod/Efficient-Apriori")
;;                (commit commit)))
;;         (file-name (git-file-name name version))
;;         (sha256
;;          (base32
;;           "0dvl4l5343dvk5arfrrb2lr4bxz0kaf45wa4ph13r7mi4nqg0ayw"))))
;;    (build-system python-build-system)
;;    (arguments
;;     `(#:tests? #f))
;;    (home-page
;; 	"https://github.com/tommyod/Efficient-Apriori")
;;    (synopsis
;; 	"An efficient Python implementation of the Apriori algorithm.")
;;    (description
;; 	"An efficient Python implementation of the Apriori algorithm.")
;;    (license license:expat))))

(concatenate-manifests
 (list
  (packages->manifest
   (list python-tweepy))
  (specifications->manifest
   '("fd"
     "graphviz"
     "guile"
     "guile-sparql"
     "python-numpy"
     "python-rdflib"
     "python-requests"
     "python-wrapper"
     "raptor2"
     "ripgrep"))))
