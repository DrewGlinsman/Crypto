# Crypto-master
Explanation of the main bot:

SuperTrainer will run multiple versions of CryptoTrainer
corresponding to the website, day, hour, and min associated with the test.
Each CryptoTrainer used will be pulled from the STORAGE directory 
and temporarily placed in the TRAINING directory while the training
is ongoing. Each CryptoTrainer is selected at random from the 
set of stored superparam files in the STORAGE directory. 
Each CryptoTrainer can either be an original, non-randomized file
OR it can be a randomized version of an original. Each CryptoTrainer
is also in STORAGE with a directory of associated CryptoEvaluator files. 
With each training set, a CryptoTrainer placed in TRAINING will bring
with it a particular one of its STORAGE CryptoEvaluators. Each CryptoTrainer
will setup a training session with a number of classes and variations. 
The difference is each class will include a number of variations of
the original CryptoEvaluator CryptoTrainer brought with it. 
After each class tests all the variations the best one is kept and then
used to start a new class. After all the tests are run, the results are
stored in CryptoTrainer (i.e. how well the variations of all classes
did) and then the SuperTrainer will determine whether the CryptoEvalutor
that was developed after training was better than the one it was made from.
Furthermore, the SuperTrainer will determine whether the CrypoTrainer
produced better results than its original (if it was edited). 
