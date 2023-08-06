    def ReadSettings( self ):
        """Read header from an annotation file."""

        # first line says "mtrax header\n"
        line = self.file.readline() 
        if line == 'mtrax header\n':
            pass
        elif line == 'Ctrax header\n':
            pass
        else:
            print "line = >" + line + "<"
            raise InvalidFileFormatException("Annotation file does not start with 'Ctrax header' or 'mtrax header'")
        
        # next lines have parameters.
        while True:
            line = self.file.readline()
            # header ends when we see 'end header\n'
            if line == '':
                raise InvalidFileFormatException("End of Annotation File reached; did not find 'end header'")
            if line == 'end header\n':
                self.start_data = self.file.tell()
                break
            # split into parameter and value at :
            words = line.split(':',1)
            if len(words) is not 2:
                raise InvalidFileFormatException("More than one ':' in line >> " + line)
            parameter = words[0]
            value = words[1]
            # strip the \n
            if value[-1] == '\n':
                value = value[:-1]
            else:
                raise InvalidFileFormatException("Line does not end in newline character. line >> " + line)
            if len(value) == 0:
                continue
            if parameter == 'bg_type':
                params.bg_type = float(value)
            elif parameter == 'n_bg_std_thresh':
                params.n_bg_std_thresh = float(value)
            elif parameter == 'n_bg_std_thresh_low':
                params.n_bg_std_thresh_low = float(value)
            elif parameter == 'bg_std_min':
                params.bg_std_min = float(value)
            elif parameter == 'bg_std_max':
                params.bg_std_max = float(value)
            elif parameter == 'n_bg_frames':
                params.n_bg_frames = int(value)
            elif parameter == 'min_nonarena':
                params.min_nonarena = float(value)                
            elif parameter == 'max_nonarena':
                params.max_nonarena = float(value)
            elif parameter == 'arena_center_x':
                params.arena_center_x = float(value)
            elif parameter == 'arena_center_y':
                params.arena_center_y = float(value)
            elif parameter == 'arena_radius':
                params.arena_radius = float(value)
            elif parameter == 'do_set_circular_arena':
                params.do_set_circular_arena = num.bool(value)
            elif parameter == 'do_use_morphology':
                params.do_use_morphology = num.bool(value)
            elif parameter == 'opening_radius':
                params.opening_radius = int(value)
            elif parameter == 'closing_radius':
                params.closing_radius = int(value)
            elif parameter == 'bg_algorithm':
                if value == 'median':
                    params.use_median = True
                else:
                    params.use_median = False
            # note that when loading settings, the background model is not
            # read in
            elif parameter == 'background median':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'background mean':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'bg_norm_type':
                params.bg_norm_type = int(value)
            elif parameter == 'background mad':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'background std':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'hfnorm':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'roipolygons':
                sz = int(value)
                self.file.seek(sz,1)
            elif parameter == 'hm_cutoff':
                params.hm_cutoff = float(value)
            elif parameter == 'hm_boost':
                params.hm_boost = int(value)
            elif parameter == 'hm_order':
                params.hm_order = int(value)
            elif parameter == 'maxarea':
                params.maxshape.area = float(value)
            elif parameter == 'maxmajor':
                params.maxshape.major = float(value)
            elif parameter == 'maxminor':
                params.maxshape.minor = float(value)
            elif parameter == 'maxecc':
                params.maxshape.ecc = float(value)
            elif parameter == 'minarea':
                params.minshape.area = float(value)
            elif parameter == 'minmajor':
                params.minshape.major = float(value)
            elif parameter == 'minminor':
                params.minshape.minor = float(value)
            elif parameter == 'minecc':
                params.minshape.ecc = float(value)
            elif parameter == 'meanarea':
                params.meanshape.area = float(value)
            elif parameter == 'meanmajor':
                params.meanshape.major = float(value)
            elif parameter == 'meanminor':
                params.meanshape.minor = float(value)
            elif parameter == 'meanecc':
                params.meanshape.ecc = float(value)
            elif parameter == 'nframes_size':
                params.n_frames_size = int(value)
            elif parameter == 'nstd_shape':
                params.n_std_thresh = float(value)
            elif parameter == 'max_jump':
                params.max_jump = float(value)
                self.max_jump = params.max_jump
            elif parameter == 'ang_dist_wt':
                params.ang_dist_wt = float(value)
            elif parameter == 'center_dampen':
                params.dampen = float(value)
            elif parameter == 'angle_dampen':
                params.angle_dampen = float(value)
            elif parameter == 'velocity_angle_weight':
                params.velocity_angle_weight = float(value)
            elif parameter == 'max_velocity_angle_weight':
                params.max_velocity_angle_weight = float(value)
            elif parameter == 'minbackthresh':
                params.minbackthresh = float(value)
            elif parameter == 'maxpenaltymerge':
                params.maxpenaltymerge = float(value)
            elif parameter == 'maxareadelete':
                params.maxareadelete = float(value)
            elif parameter == 'minareaignore':
                params.minareaignore = float(value)
            elif parameter == 'data format':
                self.n_fields = len(value.split())
            elif parameter == 'movie_name':
                params.annotation_movie_name = value
