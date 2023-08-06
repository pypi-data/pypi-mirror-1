/* A Bison parser, made by GNU Bison 2.3.  */

/* Skeleton interface for Bison's Yacc-like parsers in C

   Copyright (C) 1984, 1989, 1990, 2000, 2001, 2002, 2003, 2004, 2005, 2006
   Free Software Foundation, Inc.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2, or (at your option)
   any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor,
   Boston, MA 02110-1301, USA.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     COLON = 1018,
     DOT = 1019,
     ERROR_TOKEN = 1020,
     BOOLEAN = 1021,
     NUMBER = 1022,
     INITSWSTATE = 1023,
     STRING = 1024,
     PREFGEOMETRY = 1025,
     GEOMSPEC = 1026,
     GEOMFULL = 1027,
     STYLE = 1028,
     ACCEL = 1029,
     ACCELNAME = 1030,
     COLOR = 1031,
     COLORNAME = 1032,
     BACK = 1033,
     FORE = 1034,
     EXIT_ON_SAME = 1000,
     EXIT_IF_NO_CONFLICTS = 1001,
     EXIT_WITH_MERGE_STATUS = 1002,
     SELECT_MERGE = 1003,
     IGNORE_HORIZONTAL_WS = 1004,
     IGNORE_PERHUNK_WS = 1005,
     FORMAT_CLIPBOARD_TEXT = 1006,
     IGNORE_ERRORS = 1007,
     WARN_ABOUT_UNSAVED = 1008,
     DISABLE_CURSOR_DISPLAY = 1009,
     DRAW_PATTERN_IN_FILLER_LINES = 1010,
     HIDE_CR = 1011,
     DIRDIFF_IGNORE_FILE_CHANGES = 1012,
     DIRDIFF_BUILD_FROM_OUTPUT = 1013,
     DIRDIFF_RECURSIVE = 1014,
     NULL_HORIZONTAL_MARKERS = 1015,
     USE_INTERNAL_DIFF = 1016,
     FONT_APP = 1035,
     FONT_TEXT = 1036,
     COMMAND = 1037,
     COMMANDNAME = 1038,
     COMMANDSW = 1039,
     COMMANDSWNAME = 1040,
     INITSW = 1041,
     INITSWNAME = 1042,
     TAG = 1043,
     TAGNAME = 1044,
     SHOW = 1045,
     SHOWNAME = 1046,
     TAB_WIDTH = 1047,
     OVERVIEW_FILE_WIDTH = 1048,
     OVERVIEW_SEP_WIDTH = 1049,
     VERTICAL_LINE_POS = 1050,
     CLIPBOARD_HEAD_FORMAT = 1051,
     CLIPBOARD_LINE_FORMAT = 1052,
     HORDIFF_TYPE = 1053,
     HORDIFF = 1054,
     HORDIFF_MAX = 1055,
     HORDIFF_CONTEXT = 1056,
     SHOW_PANE_MERGED_VIEW_PERCENT = 1057,
     MERGED_FILENAME = 1058
   };
#endif
/* Tokens.  */
#define COLON 1018
#define DOT 1019
#define ERROR_TOKEN 1020
#define BOOLEAN 1021
#define NUMBER 1022
#define INITSWSTATE 1023
#define STRING 1024
#define PREFGEOMETRY 1025
#define GEOMSPEC 1026
#define GEOMFULL 1027
#define STYLE 1028
#define ACCEL 1029
#define ACCELNAME 1030
#define COLOR 1031
#define COLORNAME 1032
#define BACK 1033
#define FORE 1034
#define EXIT_ON_SAME 1000
#define EXIT_IF_NO_CONFLICTS 1001
#define EXIT_WITH_MERGE_STATUS 1002
#define SELECT_MERGE 1003
#define IGNORE_HORIZONTAL_WS 1004
#define IGNORE_PERHUNK_WS 1005
#define FORMAT_CLIPBOARD_TEXT 1006
#define IGNORE_ERRORS 1007
#define WARN_ABOUT_UNSAVED 1008
#define DISABLE_CURSOR_DISPLAY 1009
#define DRAW_PATTERN_IN_FILLER_LINES 1010
#define HIDE_CR 1011
#define DIRDIFF_IGNORE_FILE_CHANGES 1012
#define DIRDIFF_BUILD_FROM_OUTPUT 1013
#define DIRDIFF_RECURSIVE 1014
#define NULL_HORIZONTAL_MARKERS 1015
#define USE_INTERNAL_DIFF 1016
#define FONT_APP 1035
#define FONT_TEXT 1036
#define COMMAND 1037
#define COMMANDNAME 1038
#define COMMANDSW 1039
#define COMMANDSWNAME 1040
#define INITSW 1041
#define INITSWNAME 1042
#define TAG 1043
#define TAGNAME 1044
#define SHOW 1045
#define SHOWNAME 1046
#define TAB_WIDTH 1047
#define OVERVIEW_FILE_WIDTH 1048
#define OVERVIEW_SEP_WIDTH 1049
#define VERTICAL_LINE_POS 1050
#define CLIPBOARD_HEAD_FORMAT 1051
#define CLIPBOARD_LINE_FORMAT 1052
#define HORDIFF_TYPE 1053
#define HORDIFF 1054
#define HORDIFF_MAX 1055
#define HORDIFF_CONTEXT 1056
#define SHOW_PANE_MERGED_VIEW_PERCENT 1057
#define MERGED_FILENAME 1058




#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE
#line 24 "resParser.y"
{
    int   num;
    char* str;
}
/* Line 1489 of yacc.c.  */
#line 174 "y.tab.h"
	YYSTYPE;
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
# define YYSTYPE_IS_TRIVIAL 1
#endif



