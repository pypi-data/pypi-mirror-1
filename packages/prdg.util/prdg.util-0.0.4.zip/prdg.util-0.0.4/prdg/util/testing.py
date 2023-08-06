class UtilTestCaseMixin(object):
    
    def assertAttributes(self, obj, dictionary):
        """Fail unless obj.k == dictionary[k] for every k in dictionary."""
        for (k, v) in dictionary.iteritems():
            self.assertEqual(getattr(obj, k), dictionary[k])