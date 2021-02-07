(use-modules (guix download)
             (guix git-download)
             (guix packages)
             ((guix licenses) #:prefix license:)
             (guix build-system gnu)
             (guix build-system python)
             (gnu packages python-check)
             (gnu packages check)
             (gnu packages python-web)
             (gnu packages python-xyz))

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

(concatenate-manifests
 (list
  (packages->manifest
   (list python-pyfim
         python-tweepy))
  (specifications->manifest
   '("fd"
     "graphviz"
     "guile"
     "guile-config"
     "guile-sparql"
     "guix"
     "gwl"
     "make"
     "parallel"
     "pbzip2"
     "python-numpy"
     "python-rdflib"
     "python-requests"
     "python-sqlalchemy"
     "python-wrapper"
     "raptor2"
     "ripgrep"))))
