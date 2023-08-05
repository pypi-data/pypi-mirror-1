##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os 
import zc.buildout
import zc.recipe.egg


class Recipe:

    def __init__(self, buildout, name, options):
        self.egg      = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout = buildout
        self.options  = options
        self.name     = name

    def install(self):
        options = self.options
        #TODO: check here that zope-instance-location is a good zope2instance folder !
        etc_folder = os.path.join(options['zope-instance-location'], 'etc')
        if not os.path.isdir(etc_folder):
            raise "%s is not a folder" % etc_folder
        # Make a new atcontenttypes.conf based on options in buildout.cfg
        self.build_atct_conf(etc_folder)

    def update(self):
        # Always regenerate the configuration file
        self.install()

    def build_atct_conf(self, etc_folder):
        """Create an atcontenttypes.conf file
        """
        # Initilize default config to match http://dev.plone.org/collective/browser/ATContentTypes/trunk/etc/atcontenttypes.conf.in
        content_type_options = { 'ATDocument': {}
                               , 'ATEvent'   : {}
                               , 'ATNewsItem': {}
                               , 'ATFile'    : {}
                               , 'ATImage'   : {}
                               }
        DEFAULT_CT_OPTIONS = { 'max-file-size'      : "no"
                             , 'max-image-dimension': "0,0"
                             }
        # Calculate per-content-type options based on user config
        for opt_name in DEFAULT_CT_OPTIONS.keys():        
            opt_items = self.options.get(opt_name, '').split('\n')
            opt_items = [i.strip() for i in opt_items if i.strip()]
            for i in opt_items:
                (ct, v) = i.split(':', 1)
                content_type_options[ct.strip()][opt_name] = v.strip()
        # Make sure each content type get default value
        for (ct, ct_options) in content_type_options.items():
            normalized_options = DEFAULT_CT_OPTIONS.copy()
            normalized_options.update(ct_options)
            content_type_options[ct] = normalized_options
        # Build the atcontenttypes.conf file based on previous calculated values
        option_map = {
            'at-news-item-max-file-size'      : content_type_options['ATNewsItem']['max-file-size']
          , 'at-news-item-max-image-dimension': content_type_options['ATNewsItem']['max-image-dimension']
          , 'at-file-max-file-size'           : content_type_options['ATFile']['max-file-size']
          , 'at-image-max-file-size'          : content_type_options['ATImage']['max-file-size']
          , 'at-image-max-image-dimension'    : content_type_options['ATImage']['max-image-dimension']
          }
        atct_conf = atct_template % option_map
        # Overwrite ATCT conf file
        conf_file = os.path.join(etc_folder, 'atcontenttypes.conf')
        if os.path.exists(conf_file):
            os.remove(conf_file)
        open(conf_file, 'w').write(atct_conf)


# The template used to build atcontenttypes.conf
atct_template = """\
<mxtidy>
    enable           yes
    drop_font_tags   yes
    drop_empty_paras yes
    input_xml        no
    output_xhtml     yes
    quiet            yes
    show_warnings    yes
    indent_spaces    yes
    word_2000        yes
    wrap             72
    tab_size         4
    char_encoding    utf8
</mxtidy>

<feature swallowImageResizeExceptions>
  enable yes
</feature>

<pil_config>
    quality 90
    resize_algo antialias
</pil_config>

<archetype ATDocument>
  # enable upload of documents
  allow_document_upload yes

  <contenttypes>
    default text/html

    allowed text/structured
    allowed text/x-rst
    allowed text/html
    allowed text/plain
  </contenttypes>
</archetype>

<archetype ATEvent>
  # enable upload of documents
  allow_document_upload yes

  <contenttypes>
    default text/html

    allowed text/structured
    allowed text/x-rst
    allowed text/html
    allowed text/plain
  </contenttypes>
</archetype>

<archetype ATNewsItem>
  # maximum file size in byte, kb or mb
  max_file_size %(at-news-item-max-file-size)s

  # maximum image dimension (w, h)
  # 0,0 means no rescaling of the original image
  max_image_dimension %(at-news-item-max-image-dimension)s

  # enable upload of documents
  allow_document_upload yes

  <contenttypes>
    default text/html

    allowed text/structured
    allowed text/x-rst
    allowed text/html
    allowed text/plain
  </contenttypes>
</archetype>

<archetype ATFile>
  # maximum file size in byte, kb or mb
  max_file_size %(at-file-max-file-size)s
</archetype>

<archetype ATImage>
  # maximum file size in byte, kb or mb
  max_file_size %(at-image-max-file-size)s
  # maximum image dimension (w, h)
  # 0,0 means no rescaling of the original image
  max_image_dimension %(at-image-max-image-dimension)s
</archetype>
"""
