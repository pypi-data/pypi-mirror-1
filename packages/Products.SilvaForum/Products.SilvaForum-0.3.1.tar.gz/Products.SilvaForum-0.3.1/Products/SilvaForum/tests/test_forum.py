# Copyright (c) 2007-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# SilvaForum
# Python

from Products.Silva.tests import SilvaTestCase
from Testing import ZopeTestCase
from Testing.ZopeTestCase import utils
from zope.component import getMultiAdapter
from datetime import datetime
from DateTime.DateTime import DateTime
import os

ZopeTestCase.installProduct('SilvaForum')

test_path = os.path.dirname(__file__)

class SilvaForumTestCase(SilvaTestCase.SilvaTestCase):
    def afterSetUp(self):
        self.root.service_extensions.install('SilvaForum')
        self.forum = self.addObject(self.getRoot(), 'Forum', 'forum',
                                    title='Forum', product='SilvaForum')

class ForumTest(SilvaForumTestCase):
    def test_topics(self):
        self.assertEquals(0, len(self.forum.topics()))
        
        self.topic1 = self.addObject(self.forum, 'Topic', 'topic1',
                                      title='Topic 1', product='SilvaForum')
        self.assertEquals(1, len(self.forum.topics()))
    
    def test_add_topic(self):
        # see if the forum is empty like we expect
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Topic')))

        # use our method to add a topic
        newtopic = self.forum.add_topic('Topic')

        # see if the topic has been added properly
        self.assertEquals(1,
                len(self.forum.objectValues('Silva Forum Topic')))

        # also see if the thing returned is what we expect it is
        self.assertEquals('Silva Forum Topic', newtopic.meta_type)
        self.assertEquals(getattr(self.forum, newtopic.id).absolute_url(),
                          newtopic.absolute_url())
        self.assertEquals('Topic', newtopic.get_title())
        
        # test id uniqueness
        topic1 = self.forum.add_topic('this is title one')
        topic2 = self.forum.add_topic('this is title one')
        self.assertNotEquals(topic1.id, topic2.id)

    def test_generate_id(self):
        # test double strings
        topic1 = self.forum.add_topic('test one')
        topic2 = self.forum.add_topic('test one')
        self.assertNotEquals(topic1.id, topic2.id)
        
        # test unicode strings
        test_id = 'ümlauts ümlauts'
        gen_id = self.forum._generate_id('ümlauts ümlauts')
        self.assertNotEquals(gen_id, test_id)

        # test invalid characters
        test_id = 'What the @#@%##!!$#%^'
        gen_id = self.forum._generate_id(test_id)
        self.assertNotEquals(gen_id, test_id)

        t1 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo_', t1.id)

        t2 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo__2', t2.id)

        t3 = self.forum.add_topic(':) foo :)')
        self.assertEquals('foo__3', t3.id)

class TopicTest(SilvaForumTestCase):
    def afterSetUp(self):
        super(TopicTest, self).afterSetUp()
        self.topic = self.addObject(self.forum, 'Topic', 'topic',
                                     title='Topic', product='SilvaForum')
    
    def test_comments(self):
        self.assertEquals(0, len(self.topic.comments()))
        
        self.comment1 = self.addObject(self.topic, 'Comment', 'comment1',
                                       title='Comment 1', product='SilvaForum')
        self.assertEquals(1, len(self.topic.comments()))
    
    def test_add_comment(self):
        # test if the forum is empty
        self.assertEquals(0,
                len(self.forum.objectValues('Silva Forum Comment')))

        # test add_comment method
        newcomment = self.topic.add_comment('Comment', 'comment text')
        
        # see if the comment has been added properly
        self.assertEquals(1,
                len(self.topic.objectValues('Silva Forum Comment')))
    
class TopicViewTest(SilvaForumTestCase):
    def afterSetUp(self):
        super(TopicViewTest, self).afterSetUp()
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                     title='Topic', product='SilvaForum')
        self.view = getMultiAdapter((self.topic, self.app.REQUEST),
                                    name=u'view.html')

    def test_format_datetime(self):
        # XXX this needs to either be removed, or test something useful...
        dt = DateTime('2007/01/01 01:00')
        self.assertEquals('2007/01/01 01:00:00 GMT+1',
                          self.view.format_datetime(dt))

    def test_unicode_form_save_problems(self):
        self.view.request['title'] = u'F\u00fb'.encode('UTF-8')
        self.view.request['text'] = u'b\u00e4r'.encode('UTF-8')

        self.view.update()

    # test some stuff on ViewBase here...
    def test_get_batch_first_link(self):
        link = self.view.get_batch_first_link(1)
        self.assert_(link.endswith('?batch_start=0'))
        link = self.view.get_batch_first_link(0)
        self.assert_(link is None)

    def test_get_batch_last_link(self):
        link = self.view.get_batch_last_link(0, 15, 10)
        self.assert_(link.endswith('?batch_start=10'))
        link = self.view.get_batch_last_link(10, 15, 10)
        self.assert_(link is None)
        link = self.view.get_batch_last_link(0, 10, 10)
        self.assert_(link is None)

    def test_get_batch_prev_link(self):
        link = self.view.get_batch_prev_link(10, 10)
        self.assert_(link.endswith('?batch_start=0'))
        link = self.view.get_batch_prev_link(20, 10)
        self.assert_(link.endswith('?batch_start=10'))
        link = self.view.get_batch_prev_link(2, 10)
        self.assert_(link is None)

    def test_get_batch_next_link(self):
        link = self.view.get_batch_next_link(10, 25, 10)
        self.assert_(link.endswith('?batch_start=20'))
        link = self.view.get_batch_next_link(20, 25, 10)
        self.assert_(link is None)
        link = self.view.get_batch_next_link(10, 20, 10)
        self.assert_(link is None)

class CommentTest(SilvaForumTestCase):
    def afterSetUp(self):
        super(CommentTest, self).afterSetUp()
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                     title='Topic', product='SilvaForum')
        self.comment = self.addObject(self.topic, 'Comment', 'comment1',
                                      title='Comment', product='SilvaForum')

    def test_comment(self):
        self.assertEquals('Comment', self.comment.get_title())
        self.assertEquals('', self.comment.get_text())

        self.comment.set_text('foo text')
        self.assertEquals('foo text', self.comment.get_text())

class CommentViewTest(SilvaForumTestCase):
    def afterSetUp(self):
        super(CommentViewTest, self).afterSetUp()
        self.topic = self.addObject(self.forum, 'Topic', 'topic1',
                                    title='Topic', product='SilvaForum')
        self.comment = self.addObject(self.topic, 'Comment', 'comment1',
                                      title='Comment', product='SilvaForum')
        self.view = getMultiAdapter((self.comment, self.app.REQUEST),
                                    name=u'view.html')

    def test_format_text(self):
        text = 'foo bar'
        self.assertEquals('foo bar', self.view.format_text(text))
        text = 'foo\nbar'
        self.assertEquals('foo<br />bar', self.view.format_text(text))
        text = 'foo<bar'
        self.assertEquals('foo&lt;bar', self.view.format_text(text))

    def test_replace_links(self):
        text = 'aaa aaa www.link.org aaa'
        self.assertEquals('aaa aaa <a href="http://www.link.org">www.link.org</a> aaa',
                          self.view.replace_links(text))
        text = 'aa aa http://www.link.org a'
        self.assertEquals('aa aa <a href="http://www.link.org">http://www.link.org</a> a',
                          self.view.replace_links(text))
        text = 'aa aa http://link.org a'
        self.assertEquals('aa aa <a href="http://link.org">http://link.org</a> a',
                          self.view.replace_links(text))
        text = 'aa aa https://www.security.org a'
        self.assertEquals('aa aa <a href="https://www.security.org">https://www.security.org</a> a',
                          self.view.replace_links(text))
        text = 'aa aa mailto:myemail@myemail.com a'
        self.assertEquals('aa aa <a href="mailto:myemail@myemail.com">mailto:myemail@myemail.com</a> a',
                          self.view.replace_links(text))
        text = 'www.link.org.'
        self.assertEquals('<a href="http://www.link.org">www.link.org</a>.',
                          self.view.replace_links(text))
        text = '(www.link.org)'
        self.assertEquals('(<a href="http://www.link.org">www.link.org</a>)',
                          self.view.replace_links(text))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForumTest))
    suite.addTest(unittest.makeSuite(TopicTest))
    suite.addTest(unittest.makeSuite(TopicViewTest))
    suite.addTest(unittest.makeSuite(CommentTest))
    suite.addTest(unittest.makeSuite(CommentViewTest))
    return suite

