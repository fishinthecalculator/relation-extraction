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

(concatenate-manifests
 (list
  (packages->manifest
   (list python-tweepy))
  (specifications->manifest
   '("fd"
     "graphviz"
     "guile"
     "guile-sparql"
     "make"
     "python-numpy"
     "python-rdflib"
     "python-requests"
     "python-wrapper"
     "raptor2"
     "ripgrep"))))
