class TestStatefulVersioned:
    @classmethod
    def setup_class(self):
        Session.remove()
        repo.rebuild_db()
        Session.remove()
        logger.info('====== TestStatefulVersioned: start')
        rev1 = repo.new_revision()
        self.name1 = 'anna'
        p1 = Package(name=self.name1)
        t1 = Tag(name='geo')
        t2 = Tag(name='geo2')
        p1.tags.append(t1)
        p1.tags.append(t2)
        Session.commit()
        # can only get it after the flush
        self.rev1_id = rev1.id
        Session.remove()

    @classmethod
    def teardown_class(self):
        Session.remove()

    def test_1(self):
        p1 = Package.query.filter_by(name=self.name1).one()
        pkgtags = [ pt for pt in p1.tags_active ]
        assert pkgtags[0].__class__ == PackageTag
        assert pkgtags[1].__class__ == PackageTag

        logger.info('====== TestStatefulVersioned: test delete')
        temprev = repo.new_revision()
        p1.tags_active.clear()
        assert pkgtags[0].__class__ == PackageTag
        assert pkgtags[1].__class__ == PackageTag
        assert pkgtags[0].state.name == 'deleted'
        assert pkgtags[1].state.name == 'deleted'
        assert len(p1.tags) == 0


