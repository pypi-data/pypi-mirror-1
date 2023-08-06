==================
icemac.addressbook
==================

*Purpose:* Store, search and export addresses and phone numbers using
a web application.

*Status:* working prototype (preview of the real application)

.. contents::

Features
========

- store data of persons including (postal address, e-mail address,
  home page address phone number)

- assign keywords to persons

- search for persons by keyword

- export persons found by a search as XLS file

- multi-client capability

- user management (prepared)

- really good test coverage (> 96 %)

Roles
=====

Access to the address book is only granted after authentication. There
are three roles to authorize a user:

- visitor: visit all person's data, search and export

- editor: permissions of visitor + edit all person's data

- administrator: permissions of editor + create and change address books

Predefined users
================

As this version is a preview version there is no usermanagement
yet. The following predefined users exist: (<username>:<password>)

- admin:admin-ia (Role: administrator)

- editor:editor-ia (Role: editor)

- visitor: visitor-ia (Role: visitor)