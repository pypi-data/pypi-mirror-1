    def ReadAnnHeader( self ):
        """Read header from an annotation file."""

        self.file.seek(0,0)

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
                self.bg_imgs.opening_struct = self.bg_imgs.create_morph_struct(params.opening_radius)
            elif parameter == 'closing_radius':
                params.closing_radius = int(value)
                self.bg_imgs.closing_struct = self.bg_imgs.create_morph_struct(params.closing_radius)
            elif parameter == 'bg_algorithm':
                if value == 'median':
                    params.use_median = True
                else:
                    params.use_median = False
            elif parameter == 'background median':
                sz = int(value)
                self.bg_imgs.med = num.fromstring(self.file.read(sz),'<d')
                self.bg_imgs.med.shape = params.movie_size
            elif parameter == 'background mean':
                sz = int(value)
                self.bg_imgs.mean = num.fromstring(self.file.read(sz),'<d')
                self.bg_imgs.mean.shape = params.movie_size
            elif parameter == 'bg_norm_type':
                params.bg_norm_type = int(value)
            elif parameter == 'background mad':
                sz = int(value)
                self.bg_imgs.mad = num.fromstring(self.file.read(sz),'<d')
                self.bg_imgs.mad.shape = params.movie_size
            elif parameter == 'background std':
                sz = int(value)
                self.bg_imgs.std = num.fromstring(self.file.read(sz),'<d')
                self.bg_imgs.std.shape = params.movie_size
            elif parameter == 'hfnorm':
                sz = int(value)
                self.bg_imgs.hfnorm = num.fromstring(self.file.read(sz),'<d')
                self.bg_imgs.hfnorm.shape = params.movie_size
            elif parameter == 'roipolygons':
                sz = int(value)
                params.roipolygons = pickle.loads(self.file.read(sz))
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
            elif parameter == 'do_fix_split':
                params.do_fix_split = bool(value)
            elif parameter == 'splitdetection_length':
                params.splitdetection_length = int(value)
            elif parameter == 'splitdetection_cost':
                params.splitdetection_cost = float(value)
            elif parameter == 'do_fix_merged':
                params.do_fix_merged = bool(value)
            elif parameter == 'mergeddetection_length':
                params.mergeddetection_length = int(value)
            elif parameter == 'mergeddetection_distance':
                params.mergeddetection_distance = float(value)
            elif parameter == 'do_fix_spurious':
                params.do_fix_spurious = bool(value)
            elif parameter == 'spuriousdetection_length':
                params.spuriousdetection_length = int(value)
            elif parameter == 'do_fix_lost':
                params.do_fix_lost = bool(value)
            elif parameter == 'lostdetection_length':
                params.lostdetection_length = int(value)
            elif parameter == 'movie_name':
                params.annotation_movie_name = value
            elif parameter == 'start_frame':
                params.start_frame = int(value)
            elif parameter == 'data format':
                self.n_fields = len(value.split())

        self.bg_imgs.updateParameters()
