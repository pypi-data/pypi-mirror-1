MANPAGES = xylook.1 xlook.1 igwimport.1 igwextract.1 igwschlieren.1

all: $(MANPAGES)

install: all
	cp xylook.1 /usr/share/man/man1/.
	cp xlook.1 /usr/share/man/man1/.
	cp igwimport.1 /usr/share/man/man1/.
	cp igwextract.1 /usr/share/man/man1/.
	cp igwschlieren.1 /usr/share/man/man1/.

clean:
	rm *.1

xylook.1: ../igwtools/xplot.py
	help2man xylook \
		--name="displays the contents of an .xyp file"\
		--output="xylook.1" \
		--no-info

xlook.1: ../igwtools/xplot.py
	help2man xlook \
		--name="displays the contents of an .xpt file"\
		--output="xlook.1" \
		--no-info

igwextract.1: ../igwtools/igwtools.py
	help2man igwextract \
		--name="extract slices from a igwtools database"\
		--output="igwextract.1" \
		--no-info

igwimport.1: ../igwtools/igwtools.py
	help2man igwimport \
		--name="import video data into a igwtools database"\
		--output="igwimport.1" \
		--no-info

igwschlieren.1: ../igwtools/schlieren.py
	help2man igwschlieren \
		--name="compute synthetic schlieren field"\
		--output="igwschlieren.1" \
		--no-info

