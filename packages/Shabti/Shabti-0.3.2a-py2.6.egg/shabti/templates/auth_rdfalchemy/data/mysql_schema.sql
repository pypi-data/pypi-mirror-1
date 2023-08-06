SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `kb_1a1dc6d189_associativeBox` (
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
  CONSTRAINT `kb_1a1dc6d189_associativeBox_member_lookup` FOREIGN KEY (`member`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_associativeBox_class_lookup` FOREIGN KEY (`class`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_associativeBox_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_1a1dc6d189_identifiers` (
  `id` bigint(20) unsigned NOT NULL,
  `term_type` enum('U','B','F','V','L') collate utf8_unicode_ci NOT NULL,
  `lexical` text collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `termTypeIndex` (`term_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_1a1dc6d189_literalProperties` (
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
  CONSTRAINT `kb_1a1dc6d189_literalProperties_subject_lookup` FOREIGN KEY (`subject`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_literalProperties_predicate_lookup` FOREIGN KEY (`predicate`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_literalProperties_object_lookup` FOREIGN KEY (`object`) REFERENCES `kb_1a1dc6d189_literals` (`id`),
  CONSTRAINT `kb_1a1dc6d189_literalProperties_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_1a1dc6d189_literals` (
  `id` bigint(20) unsigned NOT NULL,
  `lexical` text collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_1a1dc6d189_namespace_binds` (
  `prefix` varchar(20) collate utf8_unicode_ci NOT NULL,
  `uri` text collate utf8_unicode_ci,
  PRIMARY KEY  (`prefix`),
  UNIQUE KEY `prefix` (`prefix`),
  KEY `uri_index` (`uri`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `kb_1a1dc6d189_relations` (
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
  CONSTRAINT `kb_1a1dc6d189_relations_subject_lookup` FOREIGN KEY (`subject`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_relations_predicate_lookup` FOREIGN KEY (`predicate`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_relations_object_lookup` FOREIGN KEY (`object`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`),
  CONSTRAINT `kb_1a1dc6d189_relations_context_lookup` FOREIGN KEY (`context`) REFERENCES `kb_1a1dc6d189_identifiers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


SET FOREIGN_KEY_CHECKS = 1;
