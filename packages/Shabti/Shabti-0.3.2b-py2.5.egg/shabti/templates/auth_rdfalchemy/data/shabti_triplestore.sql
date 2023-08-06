SET NAMES latin1;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `kb_bec6803d52_associativeBox` (
  `member` bigint(20) unsigned NOT NULL,
  `member_term` enum('U','B','F','V') collate utf8_unicode_ci NOT NULL,
  `class` bigint(20) unsigned NOT NULL,
  `class_term` enum('U','B','V') collate utf8_unicode_ci NOT NULL,
  `context` bigint(20) unsigned NOT NULL,
  `context_term` enum('U','B','F') collate utf8_unicode_ci NOT NULL,
  KEY `memberIndex` (`member`),
  KEY `member_termIndex` (`member_term`),
  KEY `classIndex` (`class`),
  KEY `class_termIndex` (`class_term`),
  KEY `contextIndex` (`context`),
  KEY `context_termIndex` (`context_term`),
  CONSTRAINT `kb_bec6803d52_associativeBox_member_lookup` FOREIGN KEY (`member`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_associativeBox_class_lookup` FOREIGN KEY (`class`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_associativeBox_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_bec6803d52_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_bec6803d52_identifiers` (
  `id` bigint(20) unsigned NOT NULL,
  `term_type` enum('U','B','F','V','L') collate utf8_unicode_ci NOT NULL,
  `lexical` text collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `termTypeIndex` (`term_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

insert into `kb_bec6803d52_identifiers` values('8385570487501145','U','http://purl.org/dc/elements/1.1/description'),
 ('16642153850084375','U','http://example.org/user/gjh'),
 ('362494727577223018','U','http://islab.hanyang.ac.kr/damls/User.daml#Password'),
 ('2524614099473811404','U','http://example.org/user/admin'),
 ('6892656741705206376','U','http://www.w3.org/2001/XMLSchema#dateTime'),
 ('-8975679327024973373','U','http://www.w3.org/2001/XMLSchema#integer'),
 ('-8502590516378968008','B','iEkridJG7'),
 ('-7571812295170462591','U','http://www.w3.org/2001/XMLSchema#boolean'),
 ('-7467428057111190211','U','http://xmlns.com/foaf/0.1/mbox'),
 ('-4004496847858620221','U','http://purl.org/dc/terms/created'),
 ('-2694610917488383574','U','http://xmlns.com/foaf/0.1/name'),
 ('-708466866507194509','U','http://xmlns.com/foaf/0.1/Person'),
 ('-58535354662726423','U','http://example.org/group/admingrp');

CREATE TABLE `kb_bec6803d52_literalProperties` (
  `subject` bigint(20) unsigned NOT NULL,
  `subject_term` enum('U','B','F','V') collate utf8_unicode_ci NOT NULL,
  `predicate` bigint(20) unsigned NOT NULL,
  `predicate_term` enum('U','V') collate utf8_unicode_ci NOT NULL,
  `object` bigint(20) unsigned NOT NULL,
  `context` bigint(20) unsigned NOT NULL,
  `context_term` enum('U','B','F') collate utf8_unicode_ci NOT NULL,
  `data_type` bigint(20) unsigned default NULL,
  `language` varchar(3) collate utf8_unicode_ci default NULL,
  KEY `subjectIndex` (`subject`),
  KEY `subject_termIndex` (`subject_term`),
  KEY `predicateIndex` (`predicate`),
  KEY `predicate_termIndex` (`predicate_term`),
  KEY `objectIndex` (`object`),
  KEY `contextIndex` (`context`),
  KEY `context_termIndex` (`context_term`),
  KEY `data_typeIndex` (`data_type`),
  KEY `languageIndex` (`language`),
  CONSTRAINT `kb_bec6803d52_literalProperties_subject_lookup` FOREIGN KEY (`subject`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_literalProperties_predicate_lookup` FOREIGN KEY (`predicate`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_literalProperties_object_lookup` FOREIGN KEY (`object`) REFERENCES `kb_bec6803d52_literals` (`id`),
  CONSTRAINT `kb_bec6803d52_literalProperties_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_bec6803d52_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

insert into `kb_bec6803d52_literalProperties` values('2524614099473811404','U','-2694610917488383574','U','1567001683823705601','-8502590516378968008','B',null,null),
 ('2524614099473811404','U','-4004496847858620221','U','1847388705172383813','-8502590516378968008','B','6892656741705206376',null),
 ('2524614099473811404','U','-7571812295170462591','U','-7495700104927381387','-8502590516378968008','B','-8975679327024973373',null),
 ('2524614099473811404','U','362494727577223018','U','1567001683823705601','-8502590516378968008','B',null,null),
 ('2524614099473811404','U','-7467428057111190211','U','3463429293375091168','-8502590516378968008','B',null,null),
 ('16642153850084375','U','-2694610917488383574','U','-1267322355139624491','-8502590516378968008','B',null,null),
 ('16642153850084375','U','-4004496847858620221','U','-4558277269575858781','-8502590516378968008','B','6892656741705206376',null),
 ('16642153850084375','U','-7571812295170462591','U','-7495700104927381387','-8502590516378968008','B','-8975679327024973373',null),
 ('16642153850084375','U','362494727577223018','U','2253637817805370469','-8502590516378968008','B',null,null),
 ('16642153850084375','U','-7467428057111190211','U','-3860992989989096352','-8502590516378968008','B',null,null),
 ('-58535354662726423','U','-7571812295170462591','U','-7495700104927381387','-8502590516378968008','B','-8975679327024973373',null),
 ('-58535354662726423','U','-4004496847858620221','U','4752074604856517674','-8502590516378968008','B','6892656741705206376',null),
 ('-58535354662726423','U','8385570487501145','U','-6700410730350429301','-8502590516378968008','B',null,null);

CREATE TABLE `kb_bec6803d52_literals` (
  `id` bigint(20) unsigned NOT NULL,
  `lexical` text collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

insert into `kb_bec6803d52_literals` values('1567001683823705601','d033e22ae348aeb5660fc2140aec35850c4da997'),
 ('1847388705172383813','2008-09-23T05:33:12.189666'),
 ('2253637817805370469','5ca27e75aea3e5e83a04c6cfa5f1b63d358cd03d'),
 ('3463429293375091168','admin@example.org'),
 ('4752074604856517674','2008-09-23T05:33:12.222554'),
 ('-7495700104927381387','1'),
 ('-6700410730350429301','Administration group'),
 ('-4558277269575858781','2008-09-23T05:33:12.206616'),
 ('-3860992989989096352','gjh@example.org'),
 ('-1267322355139624491','gjh');

CREATE TABLE `kb_bec6803d52_namespace_binds` (
  `prefix` varchar(20) collate utf8_unicode_ci NOT NULL,
  `uri` text collate utf8_unicode_ci,
  PRIMARY KEY  (`prefix`),
  UNIQUE KEY `prefix` (`prefix`),
  KEY `uri_index` (`uri`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

insert into `kb_bec6803d52_namespace_binds` values('cc','http://web.resource.org/cc/'),
 ('dc','http://purl.org/dc/elements/1.1/'),
 ('foaf','http://xmlns.com/foaf/0.1/'),
 ('purl','http://purl.org/dc/terms/'),
 ('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
 ('rdfs','http://www.w3.org/2000/01/rdf-schema#'),
 ('shgp','http://example.org/group/'),
 ('shusr','http://example.org/user/'),
 ('usr','http://islab.hanyang.ac.kr/damls/User.daml#'),
 ('xml','http://www.w3.org/XML/1998/namespace'),
 ('xmls','http://www.w3.org/2001/XMLSchema#');

CREATE TABLE `kb_bec6803d52_relations` (
  `subject` bigint(20) unsigned NOT NULL,
  `subject_term` enum('U','B','F','V') collate utf8_unicode_ci NOT NULL,
  `predicate` bigint(20) unsigned NOT NULL,
  `predicate_term` enum('U','V') collate utf8_unicode_ci NOT NULL,
  `object` bigint(20) unsigned NOT NULL,
  `object_term` enum('U','B','F','V') collate utf8_unicode_ci NOT NULL,
  `context` bigint(20) unsigned NOT NULL,
  `context_term` enum('U','B','F') collate utf8_unicode_ci NOT NULL,
  KEY `subjectIndex` (`subject`),
  KEY `subject_termIndex` (`subject_term`),
  KEY `predicateIndex` (`predicate`),
  KEY `predicate_termIndex` (`predicate_term`),
  KEY `objectIndex` (`object`),
  KEY `object_termIndex` (`object_term`),
  KEY `contextIndex` (`context`),
  KEY `context_termIndex` (`context_term`),
  CONSTRAINT `kb_bec6803d52_relations_subject_lookup` FOREIGN KEY (`subject`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_relations_predicate_lookup` FOREIGN KEY (`predicate`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_relations_object_lookup` FOREIGN KEY (`object`) REFERENCES `kb_bec6803d52_identifiers` (`id`),
  CONSTRAINT `kb_bec6803d52_relations_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_bec6803d52_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

insert into `kb_bec6803d52_relations` values('-58535354662726423','U','-708466866507194509','U','2524614099473811404','U','-8502590516378968008','B'),
 ('-58535354662726423','U','-708466866507194509','U','16642153850084375','U','-8502590516378968008','B');

SET FOREIGN_KEY_CHECKS = 1;
