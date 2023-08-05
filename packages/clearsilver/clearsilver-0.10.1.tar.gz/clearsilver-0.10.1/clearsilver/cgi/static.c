/*
 * Copyright 2001-2004 Brandon Long
 * All Rights Reserved.
 *
 * ClearSilver Templating System
 *
 * This code is made available under the terms of the ClearSilver License.
 * http://www.clearsilver.net/license.hdf
 *
 */

#include "ClearSilver.h"

#include <unistd.h>
#include <limits.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int main (int argc, char **argv, char **envp)
{
  NEOERR *err;
  CGI *cgi;
  char *cs_file;
  char hdf_file[_POSIX_PATH_MAX];
  char *p;

  cgi_debug_init (argc,argv);
  cgiwrap_init_std (argc, argv, envp);

  err = cgi_init(&cgi, NULL);
  if (err != STATUS_OK)
  {
    cgi_neo_error(cgi, err);
    nerr_log_error(err);
    return -1;
  }

  cs_file = hdf_get_value (cgi->hdf, "CGI.PathTranslated", NULL);
  if (cs_file == NULL)
  {
    cgi_error (cgi, "No PATH_TRANSLATED var");
    return -1;
  }
  p = strrchr (cs_file, '/');
  if (p)
  {
    *p = '\0';
    err = hdf_set_value (cgi->hdf, "hdf.loadpaths.0", cs_file);
    chdir(cs_file);
    *p = '/';
    if (err)
    {
      cgi_neo_error(cgi, err);
      nerr_log_error(err);
      return -1;
    }
  }
  err = hdf_read_file (cgi->hdf, "common.hdf");
  if (err && !nerr_handle(&err, NERR_NOT_FOUND))
  {
    cgi_neo_error(cgi, err);
    nerr_log_error(err);
    return -1;
  }
  snprintf (hdf_file, sizeof(hdf_file), "%s.hdf", cs_file);
  err = hdf_read_file (cgi->hdf, hdf_file);
  if (err && !nerr_handle(&err, NERR_NOT_FOUND))
  {
    cgi_neo_error(cgi, err);
    nerr_log_error(err);
    return -1;
  }
  p = strrchr (cs_file, '.');
  if (p)
  {
    *p = '\0';
    snprintf (hdf_file, sizeof(hdf_file), "%s.hdf", cs_file);
    *p = '.';
    err = hdf_read_file (cgi->hdf, hdf_file);
    if (err && !nerr_handle(&err, NERR_NOT_FOUND))
    {
      cgi_neo_error(cgi, err);
      nerr_log_error(err);
      return -1;
    }
  }
  cs_file = hdf_get_value (cgi->hdf, "CGI.StaticContent", cs_file);
  err = cgi_display (cgi, cs_file);
  if (err != STATUS_OK)
  {
    cgi_neo_error(cgi, err);
    nerr_log_error(err);
    return -1;
  }
  return 0;
}
