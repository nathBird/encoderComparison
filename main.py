import argparse
import subprocess

# start with an arbitrary list of codecs
codecs = ["libx264"]  # "libaom-av1", "libvpx-vp9", "libx265"]
ffmpeg_bin = "ffmpeg"  # in case of different version name


class Media(object):
    def __init__(self, filename):
        self.name = filename
        self.prefix, self.extension = filename.split('.')

    def encode(self, codec):
        encoded_files = []  # empty list of encoded files corresponding to said ref sample
        compressed = Media(self.prefix + "_" + codec + "_ultrafast." + self.extension)  # name depends on media file
        encoding_args = ["-hide_banner", "-i", self.name, "-c:v", codec, "-preset", "ultrafast", compressed.name]
        subprocess.run([ffmpeg_bin] + encoding_args)
        encoded_files.append(compressed)
        return encoded_files

    def quality(self, compressed):
        quality_args = ["-hide_banner", "-i", compressed.name, "-i", self.name, "-lavfi"]
        psnr_arg = ["libvmaf=psnr=true:log_path=psnrlog.json:log_fmt=json", "-f", "null", "-"]
        ssim_arg = ["libvmaf=ssim=true:log_path=ssimlog.json:log_fmt=json", "-f", "null", "-"]
        vmaf_arg = ["libvmaf=log_path=vmaflog.json:log_fmt=json", "-f", "null", "-"]
        # PSNR
        subprocess.run([ffmpeg_bin] + quality_args + psnr_arg)
        # SSIM
        subprocess.run([ffmpeg_bin] + quality_args + ssim_arg)
        # VMAF
        subprocess.run([ffmpeg_bin] + quality_args + vmaf_arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple ffmpeg encoding comparator")
    parser.add_argument("reference", type=str, help="file to run the encoding in")
    # parser.add_argument("-v", "--verbosity", help="increase ouput verbosity")
    args = parser.parse_args()
    sample = Media(args.reference)
    for codec in codecs:
        encoded_files = sample.encode(codec)
        for file in encoded_files:
            sample.quality(file)
