Introduction
============

The default plone/zope splitters do not properly work with greek text. This product removes accents from greek strings and properly replaces them with unicode, enabling your searches to work out of the box!

Installation
============
If not using generic setup with plone:
1) Create a ZCTextIndex Lexicon from ZMI
2) Delete in the portal_catalog the indexes that contain greek text and recreate them using GRSplitter as a splitter.

If you are using generic setup profiles, here is an example snippet to help you with catalog.xml

<?xml version="1.0"?>
<object name="portal_catalog" meta_type="Plone Catalog Tool">

 <object name="gr_lexicon" meta_type="ZCTextIndex Lexicon" purge="False" >
  <element name="GR splitter" group="Word Splitter"/>
  <element name="Case Normalizer" group="Case Normalizer"/>
 </object>
 
 <index name="greekIndexExample" meta_type="ZCTextIndex" purge="False" >
  <indexed_attr value="myAttribute"/>
  <extra name="index_type" value="Okapi BM25 Rank"/>
  <extra name="lexicon_id" value="gr_lexicon"/>
 </index>

</object>
