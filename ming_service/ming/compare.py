#compare




import pickle




tmp1_hashes_name = 'fixtures/02\ White\ America.mp3_hashes'
#tmp1_hashes_name = 'fixtures/splin_-_mamma_mia_hashes'
#tmp1_hashes_name = 'tmp1_hashes'

tmp1_hashes = open(tmp1_hashes_name, 'rb')
hashes1 = pickle.load(tmp1_hashes)
tmp1_hashes.close()




#the same for test
#tmp2_hashes_name = 'fixtures/02\ White\ America.mp3_hashes'

#tmp2_hashes_name = 'tmp2_hashes'
#tmp2_hashes_name = 'fixtures/white_america_526.mp3_hashes'
#tmp2_hashes_name = 'fixtures/white_america_instrumental_511.mp3_hashes'
#tmp2_hashes_name = 'fixtures/splin_no_exit.mp3_hashes'

#tmp2_hashes_name = 'fixtures/splin_-_mamma_mia.mp3_hashes'
tmp2_hashes_name = 'fixtures/splin_-_mamma_mia_hashes'
tmp2_hashes_name = 'fixtures/splin_-_mama_miya2_hashes'


tmp2_hashes = open(tmp2_hashes_name, 'rb')
hashes2 = pickle.load(tmp2_hashes)
tmp2_hashes.close()



#print type(hashes1), len(hashes1)
#print type(hashes2), len(hashes2)

union = set()
union |= hashes2
union |= hashes1

#intersection
print '--'
print tmp1_hashes_name, ' Vs ', tmp2_hashes_name
print 'original \t\t', len(hashes1)
print 'new \t\t\t', len(hashes2)
print 'common fp\t\t', len(hashes2.intersection(hashes1))
print 'union fp\t\t', len(union)
print 'fp metric\t\t', float(len(hashes2.intersection(hashes1)))/float(len(union))
