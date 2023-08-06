from __future__ import with_statement
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from mercurial import hg, commands, ui
from meritocracy import meta
from meritocracy import models


class Meritocracy(object):
    def __init__(self, repository, workspace):
        self.ui = ui.ui()
        self.repository = hg.repository(self.ui, repository)
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        models.init_model(self.engine)
        meta.metadata.create_all(self.engine)

        with meta.Session.begin():
            repo = meta.Session.query(models.Repository).filter(models.Repository.path==repository).first()
            if not repo:
                repo = models.Repository(path=repository,current_revision=0)
                meta.Session.add(repo)
            self._update(repo)
            revstring = ''.join('%x' % ord(hexdig) for hexdig in self.repository['tip'].node())
            repo.current_revision = revstring

    def _update(self, repo):
        for revision in self.repository:
            ctxt = self.repository[revision]
            revstring = ''.join('%x' % ord(hexdig) for hexdig in ctxt.node())

            contribution = meta.Session.query(models.Contribution).filter(models.Contribution.revision==revstring).first()
            if contribution:
                continue

            try:
                username = filter(lambda x: x.startswith('http://'), ctxt.user().split())[0]
            except IndexError:
                continue
            user = meta.Session.query(models.User).filter(models.User.username == username).first()
            if not user:
                user = models.User(username=username)
                meta.Session.add(user)
            contribution = models.Contribution(repo_id=repo.id, user_id=user.id,revision=revstring)
            meta.Session.add(contribution)
    def contributions(self, username, cutoffdate):
        """Get the number of recent contributions that a user has made"""
        # cutoffdate does not currently work, we need to fix that.
        user = meta.Session.query(models.User).filter(models.User.username==username).first()
        if not user:
            return 0
        try:
            return meta.Session.query(func.count(models.Contribution.id)).filter(models.Contribution.user_id==user.id).first()[0]
        except:
            return 0
