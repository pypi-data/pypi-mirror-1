To: {{ message['from'] }}
From: {{ confirm_address }}
Subject:  Please confirm your new blog {{ post_name }}
Reply-To: {{ confirm_address }}

Hi there, you requested that I create a blog with a post named:

{{ post_name }} : {{ message['subject'] }}

Before I do that, you'll just need to confirm that you are a person and
not someone pretending to be a person.  Sure, a bot could probably
figure out how to confirm this subscription, but at a minimum we want
to make sure that you aren't at least signed up for something you don't
want.

With that in mind, simply hit reply to this message or send an email to:

{{ confirm_address }}

Once you send that then we'll make your page using your original
message.

** Don't worry, your original posting is not lost. **

We'll make it all happen right when you confirm your request.

Thanks!

---
The Lamson Project
One-Shot-Blog
http://osb.{{host}}/
